/** Screenshot / thumbnail / before-after capture from the live WebGL canvas. */
import { useEffect, useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { useStore } from '../state/store';

function downscale(dataUrl: string, w: number, h: number): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const c = document.createElement('canvas'); c.width = w; c.height = h;
      const ctx = c.getContext('2d')!;
      const s = Math.max(w / img.width, h / img.height);
      const dw = img.width * s, dh = img.height * s;
      ctx.drawImage(img, (w - dw) / 2, (h - dh) / 2, dw, dh);
      resolve(c.toDataURL('image/jpeg', 0.8));
    };
    img.src = dataUrl;
  });
}

export function Capture() {
  const { gl } = useThree();
  const req = useStore((s) => s.captureRequest);
  const pending = useRef<{ nonce: number; mode: string; stage: number; before?: string } | null>(null);
  useEffect(() => { if (req) pending.current = { nonce: req.nonce, mode: req.mode, stage: 0 }; }, [req]);

  useFrame(() => {
    const p = pending.current;
    if (!p) return;
    const st = useStore.getState();
    // stage machine: wait two frames for materials/UI to settle before reading pixels
    p.stage++;
    if (p.mode === 'download' && p.stage === 3) {
      const url = gl.domElement.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = url; a.download = `${(st.project?.name ?? 'c7-interior').replace(/[^a-z0-9-_]+/gi, '_')}-${Date.now()}.png`; a.click();
      st.notify('Screenshot saved', 'success');
      pending.current = null;
    } else if (p.mode === 'thumbnail' && p.stage === 3) {
      const url = gl.domElement.toDataURL('image/jpeg', 0.9);
      void downscale(url, 480, 270).then((t) => useStore.getState().setThumbnail(t));
      pending.current = null;
    } else if (p.mode === 'compare') {
      if (p.stage === 3) { p.before = gl.domElement.toDataURL('image/jpeg', 0.9); st.setCompareFactory(true); }
      else if (p.stage === 12) {
        const after = p.before!; const factory = gl.domElement.toDataURL('image/jpeg', 0.9);
        st.setCompareFactory(false);
        st.setCompareImages({ before: factory, after });
        pending.current = null;
      }
    }
  });
  return null;
}
