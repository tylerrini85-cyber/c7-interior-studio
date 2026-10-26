/** RGB ambient lighting zones: emissive strips plus real point lights so nearby surfaces are lit. */
import { useMemo, useRef } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { useStore, selectRenderDoc } from '../state/store';
import { ZONE_IDS, type LightMode, type ZoneId } from '../project/schema';
import { b2t } from '../scene/coords';

interface StripDef { pos: [number, number, number]; size: [number, number, number]; light: [number, number, number]; lightDist: number; }

/** Zone geometry in Blender coords (x, forward, up) converted to three.js. */
const ZONE_STRIPS: Record<ZoneId, StripDef[]> = {
  dash: [
    { pos: b2t(0.50, 0.625, 0.698), size: [0.46, 0.004, 0.006], light: b2t(0.50, 0.58, 0.66), lightDist: 1.0 },
    { pos: b2t(-0.67, 0.61, 0.698), size: [0.12, 0.004, 0.006], light: b2t(-0.62, 0.56, 0.66), lightDist: 0.8 },
  ],
  console: [
    { pos: b2t(-0.168, -0.02, 0.50), size: [0.004, 0.004, 0.86], light: b2t(-0.30, -0.02, 0.42), lightDist: 0.9 },
    { pos: b2t(0.168, -0.02, 0.50), size: [0.004, 0.004, 0.86], light: b2t(0.30, -0.02, 0.42), lightDist: 0.9 },
  ],
  'footwell.driver': [{ pos: b2t(-0.37, 0.74, 0.415), size: [0.30, 0.006, 0.01], light: b2t(-0.37, 0.65, 0.30), lightDist: 1.2 }],
  'footwell.passenger': [{ pos: b2t(0.40, 0.74, 0.415), size: [0.30, 0.006, 0.01], light: b2t(0.40, 0.65, 0.30), lightDist: 1.2 }],
  'door.driver': [{ pos: b2t(-0.675, 0.10, 0.655), size: [0.004, 0.004, 1.10], light: b2t(-0.58, 0.10, 0.60), lightDist: 1.0 }],
  'door.passenger': [{ pos: b2t(0.675, 0.10, 0.655), size: [0.004, 0.004, 1.10], light: b2t(0.58, 0.10, 0.60), lightDist: 1.0 }],
  handles: [
    { pos: b2t(-0.672, 0.47, 0.675), size: [0.004, 0.004, 0.12], light: b2t(-0.62, 0.47, 0.68), lightDist: 0.4 },
    { pos: b2t(0.672, 0.47, 0.675), size: [0.004, 0.004, 0.12], light: b2t(0.62, 0.47, 0.68), lightDist: 0.4 },
  ],
  cupholders: [
    { pos: b2t(0.0, 0.055, 0.565), size: [0.085, 0.003, 0.085], light: b2t(0.0, 0.055, 0.60), lightDist: 0.35 },
    { pos: b2t(0.0, -0.03, 0.565), size: [0.085, 0.003, 0.085], light: b2t(0.0, -0.03, 0.60), lightDist: 0.35 },
  ],
  seats: [
    { pos: b2t(-0.37, 0.0, 0.085), size: [0.40, 0.004, 0.50], light: b2t(-0.37, 0.0, 0.06), lightDist: 0.9 },
    { pos: b2t(0.37, 0.0, 0.085), size: [0.40, 0.004, 0.50], light: b2t(0.37, 0.0, 0.06), lightDist: 0.9 },
  ],
  storage: [{ pos: b2t(0.0, -0.27, 0.575), size: [0.20, 0.003, 0.30], light: b2t(0.0, -0.27, 0.62), lightDist: 0.5 }],
};

const ZONE_ORDER: Record<ZoneId, number> = { dash: 0, console: 1, 'footwell.driver': 2, 'footwell.passenger': 3, 'door.driver': 4, 'door.passenger': 5, handles: 6, cupholders: 7, seats: 8, storage: 9 };

function animate(mode: LightMode, t: number, base: THREE.Color, idx: number, speed: number, out: THREE.Color): number {
  const hsl = { h: 0, s: 0, l: 0 };
  base.getHSL(hsl);
  let bright = 1;
  switch (mode) {
    case 'solid': out.copy(base); break;
    case 'glow': out.copy(base); bright = 0.6 + 0.04 * Math.sin(t * 2.1 + idx); break;
    case 'cycle': out.setHSL((hsl.h + t * 0.05 * speed) % 1, Math.max(hsl.s, 0.8), hsl.l); break;
    case 'rainbow': out.setHSL((hsl.h + t * 0.08 * speed + idx * 0.1) % 1, 1, 0.5); break;
    case 'breathe': out.copy(base); bright = 0.25 + 0.75 * (0.5 + 0.5 * Math.sin(t * 1.6 * speed)); break;
    case 'pulse': out.copy(base); bright = Math.pow(Math.max(0, Math.sin(t * 2.2 * speed)), 6) * 0.9 + 0.1; break;
    case 'wave': out.copy(base); bright = 0.3 + 0.7 * (0.5 + 0.5 * Math.sin(t * 2 * speed - idx * 0.7)); break;
    case 'alternate': out.copy(base); bright = (Math.floor(t * 1.5 * speed) + idx) % 2 === 0 ? 1 : 0.15; break;
  }
  return bright;
}

export function LightingZones() {
  const doc = useStore(selectRenderDoc);
  const quality = useStore((s) => s.settings.quality);
  const master = doc?.lighting.master;
  const zones = doc?.lighting.zones;
  const stripMats = useRef(new Map<string, THREE.MeshBasicMaterial>());
  const lights = useRef(new Map<string, THREE.PointLight>());
  const tmp = useMemo(() => new THREE.Color(), []);
  const maxLights = quality === 'mobile' ? 2 : quality === 'balanced' ? 4 : 8;

  useFrame((state) => {
    if (!master || !zones) return;
    const t = state.clock.elapsedTime;
    for (const z of ZONE_IDS) {
      const zc = zones[z];
      const on = master.enabled && zc.enabled;
      const base = new THREE.Color(zc.color);
      const hsl = { h: 0, s: 0, l: 0 }; base.getHSL(hsl); base.setHSL(hsl.h, hsl.s * master.saturation, hsl.l);
      const bright = on ? animate(master.mode, t, base, ZONE_ORDER[z], master.speed, tmp) * zc.brightness * master.brightness : 0;
      ZONE_STRIPS[z].forEach((_, i) => {
        const key = `${z}:${i}`;
        const m = stripMats.current.get(key);
        if (m) { m.color.copy(on ? tmp : base).multiplyScalar(on ? 0.15 + 2.2 * bright : 0.0); m.visible = on; }
        const l = lights.current.get(key);
        if (l) { l.color.copy(on ? tmp : base); l.intensity = on ? bright * 0.42 : 0; }
      });
    }
  });

  if (!doc) return null;
  // Every mounted point light costs per-pixel shading on every material, so lights exist only for zones that are on.
  let lightCount = 0;
  const lightingOn = !!master?.enabled;
  return (
    <group name="lighting-zones">
      {ZONE_IDS.flatMap((z) => ZONE_STRIPS[z].map((d, i) => {
        const key = `${z}:${i}`;
        const zoneOn = lightingOn && !!zones?.[z]?.enabled;
        const withLight = zoneOn && lightCount < maxLights; if (withLight) lightCount++;
        return (
          <group key={key}>
            <mesh position={d.pos} raycast={() => {}} visible={false}>
              <boxGeometry args={d.size} />
              <meshBasicMaterial ref={(m) => { if (m) stripMats.current.set(key, m); }} color="#000000" toneMapped={false} />
            </mesh>
            {withLight && <pointLight ref={(l) => { if (l) lights.current.set(key, l); }} position={d.light} intensity={0} distance={d.lightDist} decay={2} />}
          </group>
        );
      }))}
    </group>
  );
}
