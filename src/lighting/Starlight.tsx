/** Fiber-optic style starlight headliner: points sampled on the headliner surface, twinkling in a shader. */
import { useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { useStore, selectRenderDoc } from '../state/store';
import type { MeshRegistry } from '../scene/registry';
import type { StarlightConfig } from '../project/schema';

const HEADLINER_NODES = ['roof.panel', 'roof.header', 'roof.rear_strip', 'roof.rail.driver', 'roof.rail.passenger'];

function mulberry(seed: number) { let a = seed >>> 0; return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

/** Sample N points on the given meshes according to the chosen pattern. Points are pushed 1.5 mm below the surface. */
function samplePoints(meshes: THREE.Mesh[], cfg: StarlightConfig): Float32Array {
  const r = mulberry(cfg.seed + cfg.count);
  const tris: { a: THREE.Vector3; b: THREE.Vector3; c: THREE.Vector3; area: number }[] = [];
  const bb = new THREE.Box3();
  for (const m of meshes) {
    m.updateWorldMatrix(true, false);
    const g = m.geometry; const pos = g.getAttribute('position'); const idx = g.getIndex();
    const n = idx ? idx.count : pos.count;
    for (let i = 0; i < n; i += 3) {
      const ia = idx ? idx.getX(i) : i, ib = idx ? idx.getX(i + 1) : i + 1, ic = idx ? idx.getX(i + 2) : i + 2;
      const a = new THREE.Vector3().fromBufferAttribute(pos, ia).applyMatrix4(m.matrixWorld);
      const b = new THREE.Vector3().fromBufferAttribute(pos, ib).applyMatrix4(m.matrixWorld);
      const c = new THREE.Vector3().fromBufferAttribute(pos, ic).applyMatrix4(m.matrixWorld);
      const area = new THREE.Vector3().subVectors(b, a).cross(new THREE.Vector3().subVectors(c, a)).length() / 2;
      tris.push({ a, b, c, area }); bb.expandByPoint(a).expandByPoint(b).expandByPoint(c);
    }
  }
  const out = new Float32Array(cfg.count * 3);
  if (!tris.length) return out;
  const total = tris.reduce((s, t) => s + t.area, 0);
  const ray = new THREE.Raycaster();
  const up = new THREE.Vector3(0, 1, 0);
  const project = (x: number, z: number, i: number) => {
    ray.set(new THREE.Vector3(x, bb.min.y - 0.2, z), up);
    const hit = ray.intersectObjects(meshes, false)[0];
    if (hit) { out[i * 3] = hit.point.x; out[i * 3 + 1] = hit.point.y - 0.0015; out[i * 3 + 2] = hit.point.z; return true; }
    return false;
  };
  const w = bb.max.x - bb.min.x, d = bb.max.z - bb.min.z;
  let i = 0; let guard = 0;
  while (i < cfg.count && guard++ < cfg.count * 20) {
    let ok = false;
    if (cfg.pattern === 'grid') {
      const cols = Math.ceil(Math.sqrt(cfg.count * w / d)); const rows = Math.ceil(cfg.count / cols);
      const cx = i % cols, cy = Math.floor(i / cols);
      ok = project(bb.min.x + (cx + 0.5 + (r() - 0.5) * 0.3) * w / cols, bb.min.z + (cy + 0.5 + (r() - 0.5) * 0.3) * d / Math.max(1, rows), i);
      if (!ok) { i++; continue; }
    } else if (cfg.pattern === 'spiral') {
      const t = i / cfg.count; const ang = t * Math.PI * 14; const rad = 0.05 + t * 0.5;
      ok = project((bb.min.x + bb.max.x) / 2 + Math.cos(ang) * rad * (w / 1.2) + (r() - 0.5) * 0.03, (bb.min.z + bb.max.z) / 2 + Math.sin(ang) * rad * (d / 1.2) + (r() - 0.5) * 0.03, i);
    } else if (cfg.pattern === 'milkyway') {
      // dense diagonal band plus sparse field
      const band = r() < 0.65;
      const t = r(); const x = bb.min.x + t * w; const zc = bb.min.z + (1 - t) * d * 0.7 + d * 0.15;
      ok = project(band ? x + (r() - 0.5) * 0.08 : bb.min.x + r() * w, band ? zc + (r() - 0.5) * 0.18 : bb.min.z + r() * d, i);
    } else if (cfg.pattern === 'constellation') {
      // clusters around a few anchor stars with faint connectors represented as denser points
      const anchors = 9; const k = i % anchors; const ar = mulberry(cfg.seed * 7 + k);
      const ax = bb.min.x + 0.1 * w + ar() * 0.8 * w, az = bb.min.z + 0.1 * d + ar() * 0.8 * d;
      const spread = i < anchors ? 0 : 0.12;
      ok = project(ax + (r() - 0.5) * spread, az + (r() - 0.5) * spread, i);
    } else {
      // uniform by area
      let pick = r() * total; let tri = tris[tris.length - 1];
      for (const t of tris) { pick -= t.area; if (pick <= 0) { tri = t; break; } }
      let u = r(), v = r(); if (u + v > 1) { u = 1 - u; v = 1 - v; }
      const p = tri.a.clone().multiplyScalar(1 - u - v).add(tri.b.clone().multiplyScalar(u)).add(tri.c.clone().multiplyScalar(v));
      out[i * 3] = p.x; out[i * 3 + 1] = p.y - 0.0015; out[i * 3 + 2] = p.z; ok = true;
    }
    if (ok) i++;
  }
  return out;
}

const vert = `
attribute float aPhase; attribute float aSize; attribute vec3 aColor;
uniform float uTime; uniform float uTwinkle; uniform float uSpeed; uniform float uScale; uniform float uBright;
varying vec3 vColor; varying float vAlpha;
void main(){
  float tw = 1.0 - uTwinkle * 0.5 * (1.0 + sin(uTime * (1.5 + aPhase * 2.0) * uSpeed + aPhase * 40.0));
  vColor = aColor; vAlpha = tw * uBright;
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  // fiber tips are ~1.5 mm: a few pixels at arm's length, never a blob when the camera is right under the roof
  float px = aSize * uScale * (0.9 + 0.3 * tw) * (3.2 / max(0.25, -mv.z));
  gl_PointSize = clamp(px, 1.5, 9.0);
  gl_Position = projectionMatrix * mv;
}`;
const frag = `
varying vec3 vColor; varying float vAlpha;
void main(){ vec2 c = gl_PointCoord - 0.5; float d = length(c); if (d > 0.5) discard; float a = smoothstep(0.5, 0.0, d); a = pow(a, 1.6);
  gl_FragColor = vec4(vColor * (1.0 + 0.8 * (1.0 - d * 2.0)), a * vAlpha); }`;

export function Starlight({ registry }: { registry: MeshRegistry }) {
  const doc = useStore(selectRenderDoc);
  const cfg = doc?.lighting.starlight;
  const [version, setVersion] = useState(0);
  useEffect(() => registry.subscribe(() => setVersion((v) => v + 1)), [registry]);
  const meshes = useMemo(() => HEADLINER_NODES.map((n) => registry.byNode.get(n)).filter(Boolean) as THREE.Mesh[], [registry, version]);

  const key = cfg ? `${cfg.count}|${cfg.pattern}|${cfg.seed}|${cfg.colors.join(',')}|${cfg.size}|${meshes.length}` : '';
  const geo = useMemo(() => {
    if (!cfg || !meshes.length) return null;
    const positions = samplePoints(meshes, cfg);
    const n = cfg.count; const r = mulberry(cfg.seed + 99);
    const phase = new Float32Array(n), size = new Float32Array(n), color = new Float32Array(n * 3);
    const cols = cfg.colors.map((c) => new THREE.Color(c));
    for (let i = 0; i < n; i++) {
      phase[i] = r(); size[i] = (0.6 + r() * 0.9) * cfg.size;
      const c = cols[Math.floor(r() * cols.length)] ?? cols[0]; color[i * 3] = c.r; color[i * 3 + 1] = c.g; color[i * 3 + 2] = c.b;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    g.setAttribute('aPhase', new THREE.BufferAttribute(phase, 1));
    g.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
    g.setAttribute('aColor', new THREE.BufferAttribute(color, 3));
    return g;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  const mat = useMemo(() => new THREE.ShaderMaterial({ vertexShader: vert, fragmentShader: frag, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: { uTime: { value: 0 }, uTwinkle: { value: 0.5 }, uSpeed: { value: 1 }, uScale: { value: 1 }, uBright: { value: 1 } } }), []);
  const shoot = useRef<THREE.Mesh>(null);
  const shootState = useRef({ t: 99, from: new THREE.Vector3(), to: new THREE.Vector3() });

  useFrame((state, dt) => {
    if (!cfg) return;
    mat.uniforms.uTime.value = state.clock.elapsedTime;
    mat.uniforms.uTwinkle.value = cfg.twinkle; mat.uniforms.uSpeed.value = cfg.twinkleSpeed; mat.uniforms.uBright.value = cfg.brightness;
    mat.uniforms.uScale.value = 0.9;
    const s = shootState.current;
    if (cfg.shooting && shoot.current && geo) {
      s.t += dt;
      if (s.t > 4 + Math.random() * 4) {
        const pos = geo.getAttribute('position'); const n = pos.count; if (!n) return;
        const a = Math.floor(Math.random() * n), b = Math.floor(Math.random() * n);
        s.from.fromBufferAttribute(pos, a); s.to.fromBufferAttribute(pos, b); s.t = 0;
      }
      const k = Math.min(1, s.t / 0.7);
      shoot.current.visible = k < 1;
      shoot.current.position.lerpVectors(s.from, s.to, k);
      (shoot.current.material as THREE.MeshBasicMaterial).opacity = 1 - k;
    } else if (shoot.current) shoot.current.visible = false;
  });

  if (!cfg?.enabled || !geo) return null;
  return (
    <group name="starlight">
      <points geometry={geo} material={mat} raycast={() => {}} frustumCulled={false} />
      <mesh ref={shoot} visible={false} raycast={() => {}}>
        <sphereGeometry args={[0.004, 6, 6]} />
        <meshBasicMaterial color="#ffffff" transparent toneMapped={false} />
      </mesh>
    </group>
  );
}
