/** First-person camera rig: driver/passenger POV, mouse/touch look, WASD/arrow movement, joystick, free roam with
 *  collision, inspection mode, focus animation and reset. */
import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { useFrame, useThree } from '@react-three/fiber';
import { useStore } from '../state/store';
import { CABIN_BOUNDS, DRIVER_EYE, PASSENGER_EYE } from '../scene/coords';
import type { MeshRegistry } from '../scene/registry';

/** Shared input state written by the on-screen joystick (DOM) and read by the rig. */
export const joystick = { x: 0, y: 0, active: false };
export const lookPad = { dx: 0, dy: 0 };

const keys = new Set<string>();
const isTyping = () => { const el = document.activeElement as HTMLElement | null; return !!el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT' || el.isContentEditable); };

export function CameraRig({ registry }: { registry: MeshRegistry }) {
  const { camera, gl } = useThree();
  const mode = useStore((s) => s.cameraMode);
  const setMode = useStore((s) => s.setCameraMode);
  const resetNonce = useStore((s) => s.cameraResetNonce);
  const focusTarget = useStore((s) => s.focusTarget);
  const settings = useStore((s) => s.settings);
  const eyeHeight = useStore((s) => s.project?.camera.eyeHeight ?? 0);
  const projFov = useStore((s) => s.project?.camera.fov ?? 75);
  const showroom = useStore((s) => s.showroom);
  const uiHidden = useStore((s) => s.uiHidden);

  const st = useRef({
    pos: new THREE.Vector3(...DRIVER_EYE), yaw: 0, pitch: -0.12, fov: 75,
    target: null as null | { pos: THREE.Vector3; yaw: number; pitch: number; t: number; dur: number; from: { pos: THREE.Vector3; yaw: number; pitch: number } },
    dragging: false, lastX: 0, lastY: 0, pointerId: -1, startX: 0, startY: 0, cinematicT: 0,
  });
  const ray = useRef(new THREE.Raycaster());

  const seatPos = (m: 'driver' | 'passenger') => new THREE.Vector3(...(m === 'driver' ? DRIVER_EYE : PASSENGER_EYE)).add(new THREE.Vector3(0, eyeHeight, 0));
  const tweenTo = (pos: THREE.Vector3, yaw: number, pitch: number, dur = 0.9) => {
    const s = st.current;
    s.target = { pos, yaw, pitch, t: 0, dur, from: { pos: s.pos.clone(), yaw: s.yaw, pitch: s.pitch } };
  };

  // seat buttons / reset
  useEffect(() => {
    if (mode === 'driver' || mode === 'passenger') tweenTo(seatPos(mode), 0, -0.12);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, resetNonce, eyeHeight]);

  useEffect(() => { st.current.fov = projFov; }, [projFov]);

  // test hook: lets automated render checks place the camera exactly
  useEffect(() => {
    (window as unknown as { __c7cam?: unknown }).__c7cam = {
      set: (pos: [number, number, number], yaw: number, pitch: number, fov?: number) => { const s = st.current; s.target = null; s.pos.set(...pos); s.yaw = yaw; s.pitch = pitch; if (fov) s.fov = fov; },
      get: () => ({ pos: st.current.pos.toArray(), yaw: st.current.yaw, pitch: st.current.pitch, fov: st.current.fov }),
    };
  }, []);

  // focus animation from the parts menu: aim at the point, step closer in free mode
  useEffect(() => {
    if (!focusTarget) return;
    const s = st.current;
    const p = new THREE.Vector3(...focusTarget.point);
    const from = s.pos.clone();
    const d = p.clone().sub(from);
    let dest = from;
    if (d.length() > 1.05) { dest = p.clone().sub(d.clone().normalize().multiplyScalar(0.7)); clampToCabin(dest); setMode('free'); }
    const dir = p.clone().sub(dest).normalize();
    const yaw = Math.atan2(-dir.x, -dir.z);
    const pitch = Math.asin(THREE.MathUtils.clamp(dir.y, -1, 1));
    tweenTo(dest, yaw, pitch, 0.8);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focusTarget]);

  // pointer look + wheel zoom + keys
  useEffect(() => {
    const el = gl.domElement;
    const s = st.current;
    const onDown = (e: PointerEvent) => {
      if (e.button !== 0 && e.pointerType === 'mouse') return;
      s.dragging = true; s.lastX = e.clientX; s.lastY = e.clientY; s.startX = e.clientX; s.startY = e.clientY; s.pointerId = e.pointerId;
      s.target = null;
      try { el.setPointerCapture(e.pointerId); } catch { /* ignore */ }
    };
    const onMove = (e: PointerEvent) => {
      if (!s.dragging || e.pointerId !== s.pointerId) return;
      const dx = e.clientX - s.lastX, dy = e.clientY - s.lastY;
      s.lastX = e.clientX; s.lastY = e.clientY;
      const sens = 0.0032 * settings.lookSensitivity * (e.pointerType === 'touch' ? 1.4 : 1);
      s.yaw -= dx * sens;
      s.pitch -= dy * sens * (settings.invertY ? -1 : 1);
      s.pitch = THREE.MathUtils.clamp(s.pitch, -1.35, 1.35);
    };
    const onUp = (e: PointerEvent) => { if (e.pointerId === s.pointerId) { s.dragging = false; s.pointerId = -1; } };
    const onWheel = (e: WheelEvent) => { e.preventDefault(); s.fov = THREE.MathUtils.clamp(s.fov + Math.sign(e.deltaY) * 3, 28, 100); };
    const onKey = (e: KeyboardEvent) => {
      if (isTyping()) return;
      keys.add(e.code);
      if (e.code === 'KeyR' && !e.metaKey && !e.ctrlKey) useStore.getState().resetCamera();
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Space'].includes(e.code)) e.preventDefault();
    };
    const onKeyUp = (e: KeyboardEvent) => keys.delete(e.code);
    const onBlur = () => keys.clear();
    el.addEventListener('pointerdown', onDown);
    el.addEventListener('pointermove', onMove);
    el.addEventListener('pointerup', onUp);
    el.addEventListener('pointercancel', onUp);
    el.addEventListener('wheel', onWheel, { passive: false });
    window.addEventListener('keydown', onKey);
    window.addEventListener('keyup', onKeyUp);
    window.addEventListener('blur', onBlur);
    return () => {
      el.removeEventListener('pointerdown', onDown); el.removeEventListener('pointermove', onMove); el.removeEventListener('pointerup', onUp); el.removeEventListener('pointercancel', onUp);
      el.removeEventListener('wheel', onWheel); window.removeEventListener('keydown', onKey); window.removeEventListener('keyup', onKeyUp); window.removeEventListener('blur', onBlur);
    };
  }, [gl, settings.lookSensitivity, settings.invertY]);

  const clampToCabin = (p: THREE.Vector3) => {
    p.x = THREE.MathUtils.clamp(p.x, CABIN_BOUNDS.minX, CABIN_BOUNDS.maxX);
    p.y = THREE.MathUtils.clamp(p.y, CABIN_BOUNDS.minY, CABIN_BOUNDS.maxY);
    p.z = THREE.MathUtils.clamp(p.z, CABIN_BOUNDS.minZ, CABIN_BOUNDS.maxZ);
  };

  const tryMove = (delta: THREE.Vector3, collide: boolean) => {
    const s = st.current;
    if (delta.lengthSq() < 1e-10) return;
    const next = s.pos.clone().add(delta);
    if (collide) {
      clampToCabin(next);
      const dir = delta.clone().normalize();
      const r = ray.current;
      r.set(s.pos, dir);
      r.near = 0; r.far = delta.length() + 0.09;
      const hits = r.intersectObjects(registry.solids(), false);
      if (hits.length) {
        // slide: cancel the component of motion toward the surface
        const n = hits[0].face?.normal?.clone().transformDirection(hits[0].object.matrixWorld) ?? dir.clone().negate();
        const slide = delta.clone().sub(n.multiplyScalar(delta.dot(n)));
        const next2 = s.pos.clone().add(slide); clampToCabin(next2);
        r.set(s.pos, slide.clone().normalize()); r.far = slide.length() + 0.09;
        if (slide.lengthSq() > 1e-10 && r.intersectObjects(registry.solids(), false).length === 0) s.pos.copy(next2);
        return;
      }
    }
    s.pos.copy(next);
  };

  useFrame((state, dt) => {
    const s = st.current;
    const cam = camera as THREE.PerspectiveCamera;
    dt = Math.min(dt, 0.05);
    // tween
    if (s.target) {
      s.target.t += dt;
      const k = Math.min(1, s.target.t / s.target.dur);
      const e = 1 - Math.pow(1 - k, 3);
      s.pos.lerpVectors(s.target.from.pos, s.target.pos, e);
      s.yaw = THREE.MathUtils.lerp(s.target.from.yaw, s.target.yaw, e);
      s.pitch = THREE.MathUtils.lerp(s.target.from.pitch, s.target.pitch, e);
      if (k >= 1) s.target = null;
    }
    // showroom: slow cinematic drift of the view
    if (showroom && uiHidden && !s.dragging && !s.target) {
      s.cinematicT += dt;
      s.yaw += Math.sin(s.cinematicT * 0.25) * 0.0006;
    }
    // movement input
    const fwd = new THREE.Vector3(-Math.sin(s.yaw), 0, -Math.cos(s.yaw));
    const right = new THREE.Vector3(Math.cos(s.yaw), 0, -Math.sin(s.yaw));
    const mv = new THREE.Vector3();
    const arrowsMove = settings.arrowMode === 'move';
    if (keys.has('KeyW') || (arrowsMove && keys.has('ArrowUp'))) mv.add(fwd);
    if (keys.has('KeyS') || (arrowsMove && keys.has('ArrowDown'))) mv.sub(fwd);
    if (keys.has('KeyA') || (arrowsMove && keys.has('ArrowLeft'))) mv.sub(right);
    if (keys.has('KeyD') || (arrowsMove && keys.has('ArrowRight'))) mv.add(right);
    if (keys.has('KeyE') || keys.has('Space')) mv.y += 1;
    if (keys.has('KeyQ') || keys.has('ShiftLeft') && false) mv.y -= 1;
    if (keys.has('KeyC')) mv.y -= 1;
    if (!arrowsMove) {
      const ls = 1.4 * dt;
      if (keys.has('ArrowLeft')) s.yaw += ls; if (keys.has('ArrowRight')) s.yaw -= ls;
      if (keys.has('ArrowUp')) s.pitch = Math.min(1.35, s.pitch + ls); if (keys.has('ArrowDown')) s.pitch = Math.max(-1.35, s.pitch - ls);
    }
    if (joystick.active) { mv.add(fwd.clone().multiplyScalar(-joystick.y)); mv.add(right.clone().multiplyScalar(joystick.x)); }
    if (lookPad.dx || lookPad.dy) { s.yaw -= lookPad.dx * 0.004 * settings.lookSensitivity; s.pitch = THREE.MathUtils.clamp(s.pitch - lookPad.dy * 0.004 * settings.lookSensitivity, -1.35, 1.35); lookPad.dx = 0; lookPad.dy = 0; }
    if (mv.lengthSq() > 0) {
      if (mode === 'driver' || mode === 'passenger') { setMode('free'); s.target = null; }
      const speed = (keys.has('ShiftLeft') || keys.has('ShiftRight') ? 0.9 : 0.45) * settings.moveSpeed;
      tryMove(mv.normalize().multiplyScalar(speed * dt), mode !== 'inspect');
    }
    cam.position.copy(s.pos);
    cam.rotation.set(0, 0, 0, 'YXZ');
    cam.rotation.y = s.yaw; cam.rotation.x = s.pitch;
    const targetFov = s.fov;
    if (Math.abs(cam.fov - targetFov) > 0.01) { cam.fov = THREE.MathUtils.lerp(cam.fov, targetFov, 0.2); cam.updateProjectionMatrix(); }
    const near = mode === 'inspect' ? 0.01 : 0.03;
    if (cam.near !== near) { cam.near = near; cam.updateProjectionMatrix(); }
    void state;
  });

  return null;
}
