/** Post-processing: ambient occlusion (N8AO), SMAA and a selection outline, gated by the quality preset. */
import { EffectComposer, SMAA, Outline } from '@react-three/postprocessing';
import { N8AO } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';
import { useEffect, useState } from 'react';
import * as THREE from 'three';
import { useStore } from '../state/store';
import type { MeshRegistry } from './registry';

export function Effects({ registry }: { registry: MeshRegistry }) {
  const quality = useStore((s) => s.settings.quality);
  const selected = useStore((s) => s.selected);
  const showroom = useStore((s) => s.showroom);
  const [sel, setSel] = useState<THREE.Object3D[]>([]);
  useEffect(() => {
    const update = () => {
      const next = selected && !showroom ? registry.meshesFor(selected) : [];
      setSel((prev) => (prev.length === next.length && prev.every((m, i) => m === next[i]) ? prev : next));
    };
    update();
    return registry.subscribe(update);
  }, [selected, registry, showroom]);
  if (quality === 'mobile') return null;
  // Ambient occlusion is the single most expensive pass (an M1 MacBook Air dropped from 60 to 15 fps with it on),
  // so it is reserved for Ultra and runs at half resolution there.
  const ao = quality === 'ultra';
  return (
    <EffectComposer multisampling={0} enableNormalPass={false}>
      {ao ? <N8AO aoRadius={0.16} intensity={2.0} distanceFalloff={0.5} quality="low" halfRes /> : <></>}
      <Outline selection={sel} visibleEdgeColor={0xff3b30} hiddenEdgeColor={0x661010} edgeStrength={4} blur width={1024} blendFunction={BlendFunction.SCREEN} />
      <SMAA />
    </EffectComposer>
  );
}
