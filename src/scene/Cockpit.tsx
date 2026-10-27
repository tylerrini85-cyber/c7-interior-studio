/** Loads the cockpit GLB (+ variant GLBs), registers meshes, applies materials from the project document, handles picking. */
import { useEffect, useMemo, useRef, type ReactNode } from 'react';
import * as THREE from 'three';
import { useGLTF } from '@react-three/drei';
import { useThree, type ThreeEvent } from '@react-three/fiber';
import { useStore, selectRenderDoc, variantForSlot } from '../state/store';
import { componentForNode, COMPONENT_MAP, VARIANTS, VARIANT_SLOT_NODES, type VariantSlot } from '../registry/components';
import { buildMaterial, configKey, fixedMaterialFor, stitchOverlayMaterial, MATERIAL_PRESETS } from '../materials/engine';
import { clusterTexture, controlPanelTexture, emblemTexture, infotainmentTexture, knobFaceTexture, textTexture } from '../materials/textures';
import { MeshRegistry, RegistryContext, useRegistry } from './registry';
import { SEATBACK_RECLINE } from './coords';
import type { PartConfig, ProjectDoc } from '../project/schema';

export const MODEL_BASE = `${import.meta.env.BASE_URL}models/`;
// build id appended to model urls so a normal reload always fetches new geometry (GitHub Pages caches for 10 min)
declare const __BUILD_ID__: string;
const MODEL_V = typeof __BUILD_ID__ === 'string' ? `?v=${__BUILD_ID__}` : '';

const HIDDEN_NODES = new Set(['cluster.screen', 'cluster.speedo', 'cluster.fuel', 'cluster.temp']);
const SCREEN_NODES = new Set(['cluster.glass', 'console.screen']);
const EMBROIDERY_PLACEHOLDER = /\.headrest\.embroidery$/;

function GlbGroup({ url, source, hidePrefixes: hideProp, children }: { url: string; source: string; hidePrefixes?: string[]; children?: ReactNode }) {
  const gltf = useGLTF(url);
  const registry = useRegistry();
  const hideKey = (hideProp ?? []).join('|');
  // stable identity so the registration effect only re-runs when the hidden set really changes
  const hidePrefixes = useMemo(() => (hideKey ? hideKey.split('|') : []), [hideKey]);
  const scene = useMemo(() => {
    const s = gltf.scene.clone(true);
    s.traverse((o) => {
      if ((o as THREE.Mesh).isMesh) {
        const m = o as THREE.Mesh;
        // three's GLTFLoader strips dots from node names; the Blender pipeline stores the id in extras
        const id = (m.userData?.ct_component as string | undefined) || m.name;
        m.name = id;
        m.castShadow = !m.name.startsWith('glass.');
        m.receiveShadow = true;
        if (HIDDEN_NODES.has(m.name) || EMBROIDERY_PLACEHOLDER.test(m.name)) m.visible = false;
      }
    });
    return s;
  }, [gltf]);

  useEffect(() => {
    const meshes: THREE.Mesh[] = [];
    scene.traverse((o) => {
      if (!(o as THREE.Mesh).isMesh) return;
      const m = o as THREE.Mesh;
      if (hidePrefixes.some((p) => m.name.startsWith(p))) { m.visible = false; return; }
      const comp = componentForNode(m.name);
      const matName = Array.isArray(m.material) ? m.material[0]?.name ?? '' : (m.material as THREE.Material)?.name ?? '';
      registry.register({ mesh: m, component: comp?.id ?? null, glbMaterial: matName, nodeName: m.name, source });
      meshes.push(m);
    });
    return () => { for (const m of meshes) registry.unregister(m); };
  }, [scene, registry, source, hidePrefixes]);

  return <primitive object={scene}>{children}</primitive>;
}

/** Keeps every registered mesh's material in sync with the render document. */
function MaterialSync({ doc }: { doc: ProjectDoc }) {
  const registry = useRegistry();
  const quality = useStore((s) => s.settings.quality);
  const applied = useRef(new Map<THREE.Mesh, { key: string; overlay?: THREE.Mesh; decal?: THREE.Mesh; decal2?: THREE.Mesh }>());
  const versionRef = useRef(-1);
  const lowQ = quality === 'mobile';

  useEffect(() => {
    const run = () => {
      for (const [mesh, entry] of registry.entries) {
        let cfg: PartConfig;
        let uvScale = 1;
        let allowStitch = false;
        if (entry.component && doc.parts[entry.component]) {
          cfg = doc.parts[entry.component];
          const def = COMPONENT_MAP.get(entry.component);
          allowStitch = !!def?.caps.stitch;
          if (entry.component.startsWith('steering.') || entry.component.includes('shifter')) uvScale = 1.6;
        } else {
          cfg = fixedMaterialFor(entry.glbMaterial);
        }
        // screens get their own textures
        if (SCREEN_NODES.has(entry.nodeName)) {
          const key = `screen|${doc.electronics.gaugeTheme}|${doc.electronics.gaugeColor}|${doc.electronics.infotainmentTheme}|${doc.electronics.brightness}`;
          const prev = applied.current.get(mesh);
          if (prev?.key === key) continue;
          const tex = entry.nodeName === 'cluster.glass' ? clusterTexture(doc.electronics.gaugeTheme, doc.electronics.gaugeColor, doc.electronics.brightness) : infotainmentTexture(doc.electronics.infotainmentTheme, doc.electronics.brightness);
          const m = screenMaterial(mesh, tex, doc.electronics.brightness);
          mesh.material = m;
          applied.current.set(mesh, { key });
          continue;
        }
        const key = configKey(cfg) + `|${uvScale}|${lowQ ? 'L' : 'H'}|${allowStitch ? 'S' : ''}|${cfg.text ?? ''}|${cfg.textColor ?? ''}`;
        const prev = applied.current.get(mesh);
        if (prev?.key === key) continue;
        const old = mesh.material as THREE.Material;
        const mat = buildMaterial(cfg, { uvScale, quality: lowQ ? 'low' : 'high' });
        mesh.material = mat;
        if (old && (old as THREE.Material).name !== '' && old !== mat) old.dispose?.();
        // stitch overlay (soft trims only)
        prev?.overlay?.removeFromParent(); prev?.overlay?.geometry && (prev.overlay.material as THREE.Material).dispose();
        prev?.decal?.removeFromParent();
        prev?.decal2?.removeFromParent();
        let overlay: THREE.Mesh | undefined;
        const preset = MATERIAL_PRESETS[cfg.material];
        if (allowStitch && cfg.stitch && cfg.stitch.pattern !== 'none' && (preset.group === 'Leather' || preset.group === 'Fabric & suede' || preset.group === 'Other')) {
          const om = stitchOverlayMaterial(cfg, uvScale);
          if (om) { overlay = new THREE.Mesh(mesh.geometry, om); overlay.name = '__stitch'; overlay.raycast = () => {}; mesh.add(overlay); }
        }
        let decal: THREE.Mesh | undefined;
        let decal2: THREE.Mesh | undefined;
        if (entry.nodeName === 'steering.hub') decal = makeEmblemDecal(mesh, 'hub');
        else if (entry.nodeName.endsWith('.headrest') && (!cfg.text || cfg.text.trim() === '' || cfg.text.trim() === 'C7')) decal = makeEmblemDecal(mesh, 'headrest');
        // labels sit on the key tops: 3 mm caps above the panel face (tools/blender/parts/dashboard.py CAP)
        else if (entry.nodeName === 'console.hvac') decal = makePanelDecal(mesh, controlPanelTexture(), 0.0030);
        else if (entry.nodeName.startsWith('console.hvac_knob_cap.')) decal = makePanelDecal(mesh, knobFaceTexture(entry.nodeName.endsWith('.0') ? 'temp' : 'fan'), 0.0003, thinPartNormal(mesh.geometry));
        else if (cfg.text && cfg.text.trim() && entry.component) decal = makeTextDecal(mesh, entry.component, cfg.text, cfg.textColor ?? '#c0c0c4');
        if (entry.component?.startsWith('floor.mats')) decal2 = makeEmblemDecal(mesh, 'mat');
        applied.current.set(mesh, { key, overlay, decal, decal2 });
      }
    };
    run();
    versionRef.current = registry.version;
    return registry.subscribe(run);
  }, [doc, registry, lowQ]);

  return null;
}

function screenMaterial(mesh: THREE.Mesh, tex: THREE.Texture, brightness: number): THREE.MeshPhysicalMaterial {
  // The exported cap UVs are not reliable for a planar image, so the occupant-facing face gets a fresh planar
  // projection: find the most occupant-facing normal, keep the vertices within a few degrees of it (this excludes
  // the thin side walls), project them onto that plane and normalise to [0,1] with V = 0 at the top.
  const geo = mesh.geometry;
  const uv = geo.getAttribute('uv') as THREE.BufferAttribute;
  const pos = geo.getAttribute('position') as THREE.BufferAttribute;
  // panel normal: mean of the occupant-side normals (the side walls cancel out), then the front face is the set
  // of vertices lying on the frontmost plane along that normal (smoothed vertex normals make a normal-only test unreliable)
  // panel normal: area-weighted sum of the occupant-facing triangles (the big front cap dominates the thin walls)
  const N = new THREE.Vector3(0, 0, 0);
  {
    const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), fn = new THREE.Vector3();
    const tris: THREE.Vector3[] = [];
    const index = geo.index;
    const triCount = index ? index.count / 3 : pos.count / 3;
    for (let t = 0; t < triCount; t++) {
      const i0 = index ? index.getX(t * 3) : t * 3, i1 = index ? index.getX(t * 3 + 1) : t * 3 + 1, i2 = index ? index.getX(t * 3 + 2) : t * 3 + 2;
      a.fromBufferAttribute(pos, i0); b.fromBufferAttribute(pos, i1); c.fromBufferAttribute(pos, i2);
      fn.copy(b).sub(a).cross(c.clone().sub(a));
      if (fn.z > 0) tris.push(fn.clone());
    }
    // only the large triangles (the cap) vote, so the thin walls cannot tilt the plane
    const maxLen = tris.reduce((m, v) => Math.max(m, v.length()), 0);
    for (const v of tris) if (v.length() > 0.2 * maxLen) N.add(v);
    if (N.lengthSq() < 1e-12) N.set(0, 0, 1);
  }
  N.normalize();
  const U = new THREE.Vector3(0, 1, 0).cross(N).normalize();
  const V = new THREE.Vector3().crossVectors(N, U).normalize();
  const p = new THREE.Vector3();
  let dmax = -Infinity;
  for (let i = 0; i < pos.count; i++) { p.fromBufferAttribute(pos, i); dmax = Math.max(dmax, p.dot(N)); }
  const idx: number[] = []; const us: number[] = []; const vs: number[] = [];
  for (let i = 0; i < pos.count; i++) {
    p.fromBufferAttribute(pos, i);
    if (p.dot(N) < dmax - 0.0025) continue;
    idx.push(i); us.push(p.dot(U)); vs.push(p.dot(V));
  }
  if (idx.length >= 3) {
    const minU = Math.min(...us), maxU = Math.max(...us), minV = Math.min(...vs), maxV = Math.max(...vs);
    const w = Math.max(1e-6, maxU - minU), h = Math.max(1e-6, maxV - minV);
    idx.forEach((i, k) => uv.setXY(i, (us[k] - minU) / w, (maxV - vs[k]) / h));
    uv.needsUpdate = true;
  }
  const t = tex.clone();
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  t.repeat.set(1, 1); t.offset.set(0, 0);
  t.needsUpdate = true;
  // the source canvas may still be drawing (logo image loading): re-upload this clone when it finishes
  (tex as unknown as THREE.EventDispatcher<{ imageLoaded: object }>).addEventListener('imageLoaded', () => { t.needsUpdate = true; });
  const m = new THREE.MeshPhysicalMaterial({ color: '#000000', roughness: 0.22, metalness: 0, clearcoat: 0.45, clearcoatRoughness: 0.12 });
  m.emissiveMap = t; m.emissive.set('#ffffff'); m.emissiveIntensity = 0.5 + 1.3 * brightness;
  m.name = 'screen';
  return m;
}

function makeEmblemDecal(mesh: THREE.Mesh, where: 'hub' | 'headrest' | 'mat'): THREE.Mesh {
  mesh.geometry.computeBoundingBox();
  const bb = mesh.geometry.boundingBox!;
  const c = bb.getCenter(new THREE.Vector3());
  const mat = new THREE.MeshStandardMaterial({ map: emblemTexture(), transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4, roughness: 0.35, metalness: 0.4, alphaTest: 0.05 });
  let plane: THREE.Mesh;
  if (where === 'hub') {
    // crossed flags straight on the airbag cover (IMG_4499/4516: about 58 mm wide, just above the hub centre).
    // Wheel centre and tilt come from the Blender layout (WHEEL_CENTER, WHEEL_TILT); the plane sits a hair in
    // front of the cover's apex so nothing but the artwork shows.
    plane = new THREE.Mesh(new THREE.PlaneGeometry(0.058, 0.034), mat);
    const tilt = (24 * Math.PI) / 180;
    const up = new THREE.Vector3(0, Math.cos(tilt), -Math.sin(tilt));
    const nrm = new THREE.Vector3(0, Math.sin(tilt), Math.cos(tilt));
    const hubCenter = new THREE.Vector3(-0.37, 0.705, -0.45);   // = WHEEL_CENTER in tools/blender/layout.py
    plane.position.copy(hubCenter).addScaledVector(up, 0.006).addScaledVector(nrm, 0.0358);
    plane.lookAt(plane.position.clone().add(nrm));
    void c;
  } else if (where === 'mat') {
    // embroidered flags on the mat, ahead of the CORVETTE wordmark (heel end is +z in three.js)
    plane = new THREE.Mesh(new THREE.PlaneGeometry(0.12, 0.07), mat);
    plane.position.set(c.x, bb.max.y + 0.0012, bb.max.z - 0.17);
    plane.rotation.set(-Math.PI / 2, 0, 0);
  } else {
    // flags badge at the bottom centre of the stitched headrest pad (IMG_4500): the pad leans back with the seat,
    // so step down along the pad and out along its normal from the pad's centre
    // Large badge centred on the headrest pad. The pad centre comes from the seat layout (hinge + 0.89 of the
    // backrest height along the recline axis, pad surface 0.101 m forward), only the seat's x is taken from the mesh.
    plane = new THREE.Mesh(new THREE.PlaneGeometry(0.105, 0.061), mat);
    const nrm = new THREE.Vector3(0, Math.sin(SEATBACK_RECLINE), -Math.cos(SEATBACK_RECLINE));
    // pad centre from the pad mesh itself (works for every seat variant): x and height band from its bounds,
    // z from the frontmost vertices near the centre line (frontmost is the smallest z in three.js)
    const pos = mesh.geometry.getAttribute('position');
    const cy = (bb.min.y + bb.max.y) / 2;
    let zf = Infinity;
    const p = new THREE.Vector3();
    for (let i = 0; i < pos.count; i++) { p.fromBufferAttribute(pos, i); if (Math.abs(p.x - c.x) < 0.02 && Math.abs(p.y - cy) < 0.02) zf = Math.min(zf, p.z); }
    if (!isFinite(zf)) zf = bb.min.z;
    plane.position.set(c.x, cy, zf).addScaledVector(nrm, 0.004);
    plane.lookAt(plane.position.clone().add(nrm));
  }
  plane.name = '__decal';
  plane.raycast = () => {};
  mesh.add(plane);
  return plane;
}

/** Transparent label overlay fitted to the occupant-facing face of a thin panel (same plane finding as the screens). */

/** Normal of a thin flat part (a disc, a badge): the direction in which its vertices vary least (smallest eigenvector
 *  of the position covariance, by power iteration), oriented toward the occupants (+z in three.js). */
function thinPartNormal(geo: THREE.BufferGeometry): THREE.Vector3 {
  const pos = geo.getAttribute('position') as THREE.BufferAttribute;
  const m = new THREE.Vector3(); const p = new THREE.Vector3();
  for (let i = 0; i < pos.count; i++) m.add(p.fromBufferAttribute(pos, i));
  m.divideScalar(Math.max(1, pos.count));
  let xx = 0, xy = 0, xz = 0, yy = 0, yz = 0, zz = 0;
  for (let i = 0; i < pos.count; i++) { p.fromBufferAttribute(pos, i).sub(m); xx += p.x * p.x; xy += p.x * p.y; xz += p.x * p.z; yy += p.y * p.y; yz += p.y * p.z; zz += p.z * p.z; }
  const tr = xx + yy + zz;
  // power iteration on (tr*I - C): its dominant eigenvector is C's smallest
  let v = new THREE.Vector3(0.1, 0.2, 1).normalize();
  for (let k = 0; k < 60; k++) {
    const nx = (tr - xx) * v.x - xy * v.y - xz * v.z;
    const ny = -xy * v.x + (tr - yy) * v.y - yz * v.z;
    const nz = -xz * v.x - yz * v.y + (tr - zz) * v.z;
    v = new THREE.Vector3(nx, ny, nz).normalize();
  }
  return v.z < 0 ? v.negate() : v;
}

/** Occupant-facing normal of a thin panel: area-weighted sum of its large forward-facing triangles. */
function panelFrontNormal(geo: THREE.BufferGeometry): THREE.Vector3 {
  const pos = geo.getAttribute('position') as THREE.BufferAttribute;
  const N = new THREE.Vector3(0, 0, 0);
  {
    const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), fn = new THREE.Vector3();
    const tris: THREE.Vector3[] = [];
    const index = geo.index;
    const triCount = index ? index.count / 3 : pos.count / 3;
    for (let t = 0; t < triCount; t++) {
      const i0 = index ? index.getX(t * 3) : t * 3, i1 = index ? index.getX(t * 3 + 1) : t * 3 + 1, i2 = index ? index.getX(t * 3 + 2) : t * 3 + 2;
      a.fromBufferAttribute(pos, i0); b.fromBufferAttribute(pos, i1); c.fromBufferAttribute(pos, i2);
      fn.copy(b).sub(a).cross(c.clone().sub(a));
      if (fn.z > 0) tris.push(fn.clone());
    }
    const maxLen = tris.reduce((m, v) => Math.max(m, v.length()), 0);
    for (const v of tris) if (v.length() > 0.2 * maxLen) N.add(v);
    if (N.lengthSq() < 1e-12) N.set(0, 0, 1);
  }
  return N.normalize();
}

/** Transparent label overlay fitted to the occupant-facing face of a thin panel. `normal` overrides the face
 *  direction for parts too small to find it reliably (the climate knob caps use the control panel's normal). */
function makePanelDecal(mesh: THREE.Mesh, tex: THREE.Texture, lift = 0, normal?: THREE.Vector3): THREE.Mesh {
  const geo = mesh.geometry;
  const pos = geo.getAttribute('position') as THREE.BufferAttribute;
  const N = (normal ? normal.clone() : panelFrontNormal(geo)).normalize();
  // world "up" expressed in the mesh's own frame: parts built by revolving (knobs) carry a node rotation, so a
  // local +Y would turn their labels sideways
  mesh.updateWorldMatrix(true, false);
  const upLocal = new THREE.Vector3(0, 1, 0).applyQuaternion(mesh.getWorldQuaternion(new THREE.Quaternion()).invert());
  const U = upLocal.cross(N).normalize();
  const V = new THREE.Vector3().crossVectors(N, U).normalize();
  const p = new THREE.Vector3();
  let dmax = -Infinity;
  for (let i = 0; i < pos.count; i++) { p.fromBufferAttribute(pos, i); dmax = Math.max(dmax, p.dot(N)); }
  let minU = Infinity, maxU = -Infinity, minV = Infinity, maxV = -Infinity;
  for (let i = 0; i < pos.count; i++) {
    p.fromBufferAttribute(pos, i);
    if (p.dot(N) < dmax - 0.0025) continue;
    const u = p.dot(U), v = p.dot(V);
    minU = Math.min(minU, u); maxU = Math.max(maxU, u); minV = Math.min(minV, v); maxV = Math.max(maxV, v);
  }
  const w = Math.max(0.01, maxU - minU), h = Math.max(0.01, maxV - minV);
  const mat = new THREE.MeshStandardMaterial({ map: tex, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4, roughness: 0.6, metalness: 0.1, alphaTest: 0.02 });
  const plane = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat);
  const center = new THREE.Vector3().addScaledVector(U, (minU + maxU) / 2).addScaledVector(V, (minV + maxV) / 2).addScaledVector(N, dmax + 0.0006 + lift);
  plane.position.copy(center);
  const m = new THREE.Matrix4().makeBasis(U, V, N);
  plane.quaternion.setFromRotationMatrix(m);
  plane.name = '__decal';
  plane.raycast = () => {};
  mesh.add(plane);
  return plane;
}

function makeTextDecal(mesh: THREE.Mesh, component: string, text: string, color: string): THREE.Mesh | undefined {
  mesh.geometry.computeBoundingBox();
  const bb = mesh.geometry.boundingBox!;
  const tex = textTexture(text, color);
  const mat = new THREE.MeshStandardMaterial({ map: tex, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4, roughness: 0.9 });
  let plane: THREE.Mesh;
  if (component.endsWith('.headrest')) {
    plane = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.04), mat);
    const c = bb.getCenter(new THREE.Vector3());
    // front face of the headrest (toward -z in three), leaning back with the seat
    plane.position.set(c.x, c.y + 0.005, bb.min.z - 0.002);
    plane.rotation.set(-SEATBACK_RECLINE, Math.PI, 0);
    plane.rotateY(0);
  } else if (component.startsWith('floor.mats')) {
    plane = new THREE.Mesh(new THREE.PlaneGeometry(0.26, 0.065), mat);
    const c = bb.getCenter(new THREE.Vector3());
    plane.position.set(c.x, bb.max.y + 0.0012, bb.max.z - 0.075);
    plane.rotation.set(-Math.PI / 2, 0, 0);
  } else if (component === 'sills') {
    plane = new THREE.Mesh(new THREE.PlaneGeometry(0.30, 0.05), mat);
    const c = bb.getCenter(new THREE.Vector3());
    plane.position.set(c.x, bb.max.y + 0.001, c.z);
    plane.rotation.set(-Math.PI / 2, 0, c.x < 0 ? Math.PI / 2 : -Math.PI / 2);
  } else if (component === 'console.armrest') {
    plane = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.04), mat);
    const c = bb.getCenter(new THREE.Vector3());
    plane.position.set(c.x, bb.max.y + 0.001, c.z);
    plane.rotation.set(-Math.PI / 2, 0, 0);
  } else return undefined;
  plane.name = '__decal';
  plane.raycast = () => {};
  // decal must ignore the parent's transform scale: parent is a mesh with identity transform in our export
  mesh.add(plane);
  return plane;
}

/** Hover/selection highlight via emissive tint. */
function HighlightSync() {
  const registry = useRegistry();
  const hovered = useStore((s) => s.hovered);
  const selected = useStore((s) => s.selected);
  const prev = useRef<{ mesh: THREE.Mesh; mat: THREE.MeshPhysicalMaterial }[]>([]);
  useEffect(() => {
    for (const { mat } of prev.current) { mat.emissive.set('#000000'); mat.emissiveIntensity = 1; }
    prev.current = [];
    const paint = (id: string | null, color: string, intensity: number) => {
      if (!id) return;
      for (const m of registry.meshesFor(id)) {
        const mat = m.material as THREE.MeshPhysicalMaterial;
        if (!mat || mat.name === 'screen' || !('emissive' in mat)) continue;
        mat.emissive.set(color); mat.emissiveIntensity = intensity;
        prev.current.push({ mesh: m, mat });
      }
    };
    paint(hovered && hovered !== selected ? hovered : null, '#5a1010', 0.35);
    paint(selected, '#8a1a1a', 0.5);
  }, [hovered, selected, registry, registry.version]);
  return null;
}

function Picking({ children }: { children: ReactNode }) {
  const registry = useRegistry();
  const select = useStore((s) => s.select);
  const hover = useStore((s) => s.hover);
  const compareFactory = useStore((s) => s.compareFactory);
  const showroom = useStore((s) => s.showroom);
  const last = useRef<string | null>(null);
  const { gl } = useThree();
  const compOf = (e: ThreeEvent<PointerEvent | MouseEvent>) => {
    const entry = registry.entries.get(e.object as THREE.Mesh);
    if (!entry?.component) return null;
    const def = COMPONENT_MAP.get(entry.component);
    return def ? def.id : null;
  };
  return (
    <group
      onPointerMove={(e) => {
        if (showroom) return;
        const id = compOf(e);
        if (id !== last.current) { last.current = id; hover(id); gl.domElement.style.cursor = id ? 'pointer' : ''; }
        e.stopPropagation();
      }}
      onPointerOut={() => { last.current = null; hover(null); gl.domElement.style.cursor = ''; }}
      onClick={(e) => {
        if (showroom || compareFactory) return;
        if (e.delta > 6) return; // this was a drag
        const id = compOf(e);
        e.stopPropagation();
        select(id);
      }}
      onPointerMissed={() => { /* keep selection on empty clicks */ }}
    >
      {children}
    </group>
  );
}

function VariantLoader({ slot, doc }: { slot: VariantSlot; doc: ProjectDoc }) {
  const variant = variantForSlot(doc, slot);
  const def = VARIANTS[slot].find((v) => v.id === variant);
  if (!def?.file) return null;
  return <GlbGroup url={MODEL_BASE + def.file + MODEL_V} source={`variant:${slot}:${variant}`} />;
}

export function Cockpit({ registry }: { registry: MeshRegistry }) {
  const doc = useStore(selectRenderDoc);
  if (!doc) return null;
  const hide: string[] = [];
  for (const slot of Object.keys(VARIANTS) as VariantSlot[]) {
    const v = variantForSlot(doc, slot);
    const def = VARIANTS[slot].find((x) => x.id === v);
    if (def?.file) hide.push(...VARIANT_SLOT_NODES[slot]);
  }
  return (
    <RegistryContext.Provider value={registry}>
      <Picking>
        <GlbGroup url={MODEL_BASE + 'c7-cockpit.glb' + MODEL_V} source="cockpit" hidePrefixes={hide} />
        {(Object.keys(VARIANTS) as VariantSlot[]).map((slot) => <VariantLoader key={slot} slot={slot} doc={doc} />)}
      </Picking>
      <MaterialSync doc={doc} />
      <HighlightSync />
    </RegistryContext.Provider>
  );
}

useGLTF.preload(MODEL_BASE + 'c7-cockpit.glb' + MODEL_V);
