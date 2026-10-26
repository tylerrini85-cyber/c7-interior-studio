/** Adaptive rendering: measures frame time and lowers the device pixel ratio when the GPU cannot keep up,
 *  raising it back when there is headroom. Also publishes an FPS reading for the settings page. */
import { useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { useStore } from '../state/store';

export const perf = { fps: 0, dprScale: 1 };

export function AdaptiveQuality() {
  const { setDpr, viewport } = useThree();
  const quality = useStore((s) => s.settings.quality);
  const acc = useRef({ t: 0, n: 0, scale: 1, cooldown: 0 });
  void viewport;
  useFrame((_, dt) => {
    const a = acc.current;
    a.t += dt; a.n++;
    if (a.t < 1) return;
    const fps = a.n / a.t; a.t = 0; a.n = 0;
    perf.fps = fps;
    if (a.cooldown > 0) { a.cooldown--; return; }
    const max = quality === 'ultra' ? 2 : quality === 'high' ? 1.5 : 1;
    const min = quality === 'mobile' ? 0.6 : 0.75;
    const cap = Math.min(max, window.devicePixelRatio || 1);
    let next = a.scale;
    if (fps < 28 && a.scale > min) next = Math.max(min, a.scale - 0.15);
    else if (fps > 55 && a.scale < 1) next = Math.min(1, a.scale + 0.1);
    if (next !== a.scale) { a.scale = next; perf.dprScale = next; setDpr(Math.max(0.5, cap * next)); a.cooldown = 2; }
  });
  return null;
}
