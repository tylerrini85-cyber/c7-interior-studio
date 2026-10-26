/** The 3D viewport: canvas, renderer settings, cockpit, lights, camera rig, effects, capture. */
import { Suspense, useEffect, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { useProgress } from '@react-three/drei';
import * as THREE from 'three';
import { Cockpit } from './Cockpit';
import { Environment } from './Environment';
import { Effects } from './Effects';
import { CameraRig } from '../camera/Rig';
import { LightingZones } from '../lighting/Zones';
import { Starlight } from '../lighting/Starlight';
import { Capture } from '../capture/Capture';
import { AdaptiveQuality } from '../quality/Adaptive';
import { MeshRegistry } from './registry';
import { useStore } from '../state/store';
import { DRIVER_EYE } from './coords';

function FrameCounter({ registry }: { registry: MeshRegistry }) {
  useFrame((state) => { const w = window as unknown as { __c7frames?: number; __c7scene?: unknown; __c7registry?: unknown; __c7gl?: unknown }; w.__c7frames = (w.__c7frames ?? 0) + 1; w.__c7scene = state.scene; w.__c7registry = registry; w.__c7gl = state.gl; });
  return null;
}

function LoadingBridge() {
  const { progress, active, errors, item } = useProgress();
  const setLoading = useStore((s) => s.setLoading);
  useEffect(() => {
    // deferred: drei's progress store can update while sibling components are suspending/rendering
    const t = setTimeout(() => {
      if (errors.length) { setLoading({ progress, label: 'Asset failed to load', error: errors[0] }); return; }
      setLoading(active ? { progress, label: item ? `Loading ${item.split('/').pop()}` : 'Loading cockpit' } : null);
    }, 0);
    return () => clearTimeout(t);
  }, [progress, active, errors, item, setLoading]);
  return null;
}

export function Studio3D() {
  const quality = useStore((s) => s.settings.quality);
  const registry = useMemo(() => new MeshRegistry(), []);
  const dpr: [number, number] = quality === 'ultra' ? [1, 1.5] : quality === 'high' ? [1, 1.25] : [0.75, 1];
  return (
    <Canvas
      shadows={quality !== 'mobile'}
      dpr={dpr}
      camera={{ position: DRIVER_EYE, fov: 75, near: 0.03, far: 80 }}
      gl={{ antialias: quality === 'mobile' || quality === 'balanced', powerPreference: 'high-performance', preserveDrawingBuffer: true, toneMapping: THREE.AgXToneMapping, outputColorSpace: THREE.SRGBColorSpace }}
      onCreated={({ gl }) => {
        gl.shadowMap.type = THREE.PCFShadowMap;
        gl.domElement.addEventListener('webglcontextlost', (e) => { e.preventDefault(); useStore.getState().notify('Graphics context lost. The page will recover automatically.', 'error'); });
        gl.domElement.addEventListener('webglcontextrestored', () => useStore.getState().notify('Graphics context restored', 'success'));
      }}
      style={{ touchAction: 'none' }}
    >
      <LoadingBridge />
      <FrameCounter registry={registry} />
      <Suspense fallback={null}>
        <Environment />
        <Cockpit registry={registry} />
        <LightingZones />
        <Starlight registry={registry} />
      </Suspense>
      <CameraRig registry={registry} />
      <Effects registry={registry} />
      <Capture />
      <AdaptiveQuality />
    </Canvas>
  );
}
