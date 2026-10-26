/** Procedural texture generation (canvas based, cached). Produces normal/roughness/color maps for the material engine. */
import * as THREE from 'three';

const cache = new Map<string, THREE.Texture>();

function canvas(size: number) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  return c;
}

function mulberry(seed: number) {
  let a = seed >>> 0;
  return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

/** Convert a height field (0..1 Float32Array) to a tangent-space normal map texture. */
function heightToNormal(h: Float32Array, size: number, strength: number): ImageData {
  const img = new ImageData(size, size);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const l = h[y * size + ((x - 1 + size) % size)];
      const r = h[y * size + ((x + 1) % size)];
      const u = h[((y - 1 + size) % size) * size + x];
      const d = h[((y + 1) % size) * size + x];
      const nx = (l - r) * strength;
      const ny = (u - d) * strength;
      const nz = 1;
      const len = Math.hypot(nx, ny, nz);
      const i = (y * size + x) * 4;
      img.data[i] = ((nx / len) * 0.5 + 0.5) * 255;
      img.data[i + 1] = ((ny / len) * 0.5 + 0.5) * 255;
      img.data[i + 2] = ((nz / len) * 0.5 + 0.5) * 255;
      img.data[i + 3] = 255;
    }
  }
  return img;
}

function makeTexture(key: string, size: number, draw: (ctx: CanvasRenderingContext2D, size: number) => void, opts: { color?: boolean } = {}): THREE.Texture {
  const hit = cache.get(key);
  if (hit) return hit;
  const c = canvas(size);
  const ctx = c.getContext('2d')!;
  draw(ctx, size);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.colorSpace = opts.color ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  t.anisotropy = 8;
  t.needsUpdate = true;
  cache.set(key, t);
  return t;
}

/** Fractal value noise height field. */
function noiseField(size: number, seed: number, octaves: number, baseFreq: number): Float32Array {
  const r = mulberry(seed);
  const out = new Float32Array(size * size);
  let amp = 1; let freq = baseFreq; let total = 0;
  for (let o = 0; o < octaves; o++) {
    const g = Math.max(2, Math.round(freq));
    const grid = new Float32Array((g + 1) * (g + 1));
    for (let i = 0; i < grid.length; i++) grid[i] = r();
    // wrap the grid
    for (let i = 0; i <= g; i++) { grid[i * (g + 1) + g] = grid[i * (g + 1)]; grid[g * (g + 1) + i] = grid[i]; }
    for (let y = 0; y < size; y++) {
      const fy = (y / size) * g; const y0 = Math.floor(fy); const ty = fy - y0; const sy = ty * ty * (3 - 2 * ty);
      for (let x = 0; x < size; x++) {
        const fx = (x / size) * g; const x0 = Math.floor(fx); const tx = fx - x0; const sx = tx * tx * (3 - 2 * tx);
        const a = grid[y0 * (g + 1) + x0], b = grid[y0 * (g + 1) + x0 + 1], c = grid[(y0 + 1) * (g + 1) + x0], d = grid[(y0 + 1) * (g + 1) + x0 + 1];
        const v = (a * (1 - sx) + b * sx) * (1 - sy) + (c * (1 - sx) + d * sx) * sy;
        out[y * size + x] += v * amp;
      }
    }
    total += amp; amp *= 0.5; freq *= 2;
  }
  for (let i = 0; i < out.length; i++) out[i] /= total;
  return out;
}

/** Worley (cell) noise, used for leather grain. Returns F1 distance normalized. */
function cellField(size: number, seed: number, cells: number): Float32Array {
  const r = mulberry(seed);
  const pts: [number, number][] = [];
  for (let i = 0; i < cells * cells; i++) pts.push([r(), r()]);
  const out = new Float32Array(size * size);
  const cellSize = 1 / cells;
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const px = x / size, py = y / size;
      const cx = Math.floor(px * cells), cy = Math.floor(py * cells);
      let best = 1;
      for (let oy = -1; oy <= 1; oy++) for (let ox = -1; ox <= 1; ox++) {
        const ix = (cx + ox + cells) % cells, iy = (cy + oy + cells) % cells;
        const p = pts[iy * cells + ix];
        const qx = (ix + p[0]) * cellSize + (cx + ox < 0 ? -1 : cx + ox >= cells ? 1 : 0) * 0;
        const qy = (iy + p[1]) * cellSize;
        let dx = px - qx; let dy = py - qy;
        dx -= Math.round(dx); dy -= Math.round(dy); // wrap distance
        const d = Math.hypot(dx, dy) / cellSize;
        if (d < best) best = d;
      }
      out[y * size + x] = Math.min(1, best);
    }
  }
  return out;
}

export function leatherNormal(variant: 'fine' | 'coarse' = 'fine'): THREE.Texture {
  const size = 512;
  return makeTexture(`leather_n_${variant}`, size, (ctx) => {
    const cells = cellField(size, 11, variant === 'fine' ? 40 : 22);
    const n = noiseField(size, 5, 4, 8);
    const h = new Float32Array(size * size);
    for (let i = 0; i < h.length; i++) h[i] = Math.pow(cells[i], 0.8) * 0.75 + n[i] * 0.25;
    ctx.putImageData(heightToNormal(h, size, variant === 'fine' ? 1.6 : 2.4), 0, 0);
  });
}

export function leatherRoughness(): THREE.Texture {
  const size = 256;
  return makeTexture('leather_r', size, (ctx) => {
    const n = noiseField(size, 9, 3, 6);
    const img = ctx.createImageData(size, size);
    for (let i = 0; i < size * size; i++) { const v = 150 + n[i] * 70; img.data[i * 4] = img.data[i * 4 + 1] = img.data[i * 4 + 2] = v; img.data[i * 4 + 3] = 255; }
    ctx.putImageData(img, 0, 0);
  });
}

export function perforationMaps(): { normal: THREE.Texture; roughness: THREE.Texture } {
  const size = 256;
  const draw = (ctx: CanvasRenderingContext2D, mode: 'n' | 'r') => {
    const h = new Float32Array(size * size);
    const cells = cellField(size, 11, 24);
    for (let i = 0; i < h.length; i++) h[i] = Math.pow(cells[i], 0.8) * 0.5;
    const pitch = size / 8; // 8 holes per tile
    for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
      const gx = ((x % pitch) - pitch / 2); const gy = ((y % pitch) - pitch / 2);
      const d = Math.hypot(gx, gy) / (pitch * 0.18);
      if (d < 1) h[y * size + x] = -0.8 * (1 - d * d);
    }
    if (mode === 'n') ctx.putImageData(heightToNormal(h, size, 2.2), 0, 0);
    else {
      const img = ctx.createImageData(size, size);
      for (let i = 0; i < size * size; i++) { const v = h[i] < 0 ? 230 : 160; img.data[i * 4] = img.data[i * 4 + 1] = img.data[i * 4 + 2] = v; img.data[i * 4 + 3] = 255; }
      ctx.putImageData(img, 0, 0);
    }
  };
  return { normal: makeTexture('perf_n', size, (ctx) => draw(ctx, 'n')), roughness: makeTexture('perf_r', size, (ctx) => draw(ctx, 'r')) };
}

export function alcantaraMaps(): { normal: THREE.Texture; roughness: THREE.Texture } {
  const size = 256;
  return {
    normal: makeTexture('alc_n', size, (ctx) => { const n = noiseField(size, 21, 5, 24); ctx.putImageData(heightToNormal(n, size, 0.9), 0, 0); }),
    roughness: makeTexture('alc_r', size, (ctx) => {
      const n = noiseField(size, 22, 4, 16); const img = ctx.createImageData(size, size);
      for (let i = 0; i < size * size; i++) { const v = 215 + n[i] * 40; img.data[i * 4] = img.data[i * 4 + 1] = img.data[i * 4 + 2] = v; img.data[i * 4 + 3] = 255; }
      ctx.putImageData(img, 0, 0);
    }),
  };
}

/** 2x2 twill carbon weave: normal map + a color/roughness mask with per-tow shading (so it does not read as a checkerboard). */
export function carbonTwillMaps(): { normal: THREE.Texture; color: THREE.Texture; roughness: THREE.Texture } {
  const size = 512; const tows = 16; const tow = size / tows;
  const towField = (x: number, y: number) => {
    // 2/2 twill: each tow passes over two and under two; diagonal pattern
    const i = Math.floor(x / tow), j = Math.floor(y / tow);
    const over = ((i + j) % 4) < 2; // warp over weft
    const fx = (x % tow) / tow, fy = (y % tow) / tow;
    // cylindrical tow profile across its width + fiber striations along it
    const prof = over ? Math.sin(fy * Math.PI) : Math.sin(fx * Math.PI);
    const fiber = over ? 0.08 * Math.sin(fx * Math.PI * 24) : 0.08 * Math.sin(fy * Math.PI * 24);
    return { h: prof * 0.9 + fiber, over, prof };
  };
  const normal = makeTexture('carbon_n', size, (ctx) => {
    const h = new Float32Array(size * size);
    for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) h[y * size + x] = towField(x, y).h;
    ctx.putImageData(heightToNormal(h, size, 2.5), 0, 0);
  });
  const color = makeTexture('carbon_c', size, (ctx) => {
    const img = ctx.createImageData(size, size);
    for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
      const t = towField(x, y);
      // warp and weft tows reflect light differently: subtle brightness difference + edge darkening
      const base = t.over ? 70 : 42;
      const v = base * (0.55 + 0.45 * t.prof);
      const i = (y * size + x) * 4; img.data[i] = v; img.data[i + 1] = v; img.data[i + 2] = v + 3; img.data[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
  }, { color: true });
  const roughness = makeTexture('carbon_r', size, (ctx) => {
    const img = ctx.createImageData(size, size);
    for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
      const t = towField(x, y); const v = 70 + (1 - t.prof) * 60 + (t.over ? 0 : 15);
      const i = (y * size + x) * 4; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
  });
  return { normal, color, roughness };
}

/** Forged carbon: random chopped fiber flakes. */
export function forgedCarbonMaps(): { normal: THREE.Texture; color: THREE.Texture; roughness: THREE.Texture } {
  const size = 512;
  const r = mulberry(77);
  const flakes: { x: number; y: number; a: number; l: number; w: number; b: number }[] = [];
  for (let i = 0; i < 2200; i++) flakes.push({ x: r() * size, y: r() * size, a: r() * Math.PI, l: 10 + r() * 34, w: 2 + r() * 5, b: 0.3 + r() * 0.7 });
  const paint = (ctx: CanvasRenderingContext2D, mode: 'c' | 'h') => {
    ctx.fillStyle = mode === 'c' ? '#1a1a1c' : '#808080';
    ctx.fillRect(0, 0, size, size);
    for (const f of flakes) {
      for (const [ox, oy] of [[0, 0], [size, 0], [-size, 0], [0, size], [0, -size]]) {
        ctx.save(); ctx.translate(f.x + ox, f.y + oy); ctx.rotate(f.a);
        const v = mode === 'c' ? Math.round(30 + f.b * 70) : Math.round(110 + f.b * 60);
        ctx.fillStyle = `rgb(${v},${v},${v + (mode === 'c' ? 4 : 0)})`;
        ctx.fillRect(-f.l / 2, -f.w / 2, f.l, f.w);
        ctx.restore();
      }
    }
  };
  const color = makeTexture('forged_c', size, (ctx) => paint(ctx, 'c'), { color: true });
  const normal = makeTexture('forged_n', size, (ctx) => {
    paint(ctx, 'h');
    const img = ctx.getImageData(0, 0, size, size);
    const h = new Float32Array(size * size);
    for (let i = 0; i < h.length; i++) h[i] = img.data[i * 4] / 255;
    ctx.putImageData(heightToNormal(h, size, 1.8), 0, 0);
  });
  const roughness = makeTexture('forged_r', size, (ctx) => {
    paint(ctx, 'h');
    const img = ctx.getImageData(0, 0, size, size);
    for (let i = 0; i < size * size; i++) { const v = 60 + (255 - img.data[i * 4]) * 0.35; img.data[i * 4] = img.data[i * 4 + 1] = img.data[i * 4 + 2] = v; }
    ctx.putImageData(img, 0, 0);
  });
  return { normal, color, roughness };
}

export function brushedMetalMaps(): { normal: THREE.Texture; roughness: THREE.Texture } {
  const size = 512;
  const r = mulberry(31);
  const lines = new Float32Array(size);
  for (let i = 0; i < size; i++) lines[i] = r();
  const n2 = noiseField(size, 44, 3, 4);
  return {
    normal: makeTexture('brushed_n', size, (ctx) => {
      const h = new Float32Array(size * size);
      for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) h[y * size + x] = lines[y] * 0.9 + n2[y * size + x] * 0.1;
      ctx.putImageData(heightToNormal(h, size, 0.5), 0, 0);
    }),
    roughness: makeTexture('brushed_r', size, (ctx) => {
      const img = ctx.createImageData(size, size);
      for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) { const i = (y * size + x) * 4; const v = 90 + lines[y] * 60 + n2[y * size + x] * 20; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
      ctx.putImageData(img, 0, 0);
    }),
  };
}

export function fabricMaps(): { normal: THREE.Texture; roughness: THREE.Texture } {
  const size = 256;
  return {
    normal: makeTexture('fabric_n', size, (ctx) => {
      const h = new Float32Array(size * size);
      for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) h[y * size + x] = 0.5 + 0.25 * Math.sin(x * 0.6) + 0.25 * Math.sin(y * 0.6);
      ctx.putImageData(heightToNormal(h, size, 1.4), 0, 0);
    }),
    roughness: makeTexture('fabric_r', size, (ctx) => { ctx.fillStyle = '#d8d8d8'; ctx.fillRect(0, 0, size, size); }),
  };
}

export function carpetMaps(): { normal: THREE.Texture; roughness: THREE.Texture } {
  const size = 256;
  return {
    normal: makeTexture('carpet_n', size, (ctx) => { const n = noiseField(size, 61, 5, 40); ctx.putImageData(heightToNormal(n, size, 2.0), 0, 0); }),
    roughness: makeTexture('carpet_r', size, (ctx) => { ctx.fillStyle = '#f0f0f0'; ctx.fillRect(0, 0, size, size); }),
  };
}

/** Stitch overlay: a color texture with transparent background and a dashed thread line pattern.
 *  pattern decides line layout per tile (1 m x 1 m in UV units at repeat 1). */
export function stitchMap(pattern: 'single' | 'double' | 'diamond' | 'pleat' | 'hex', color: string): THREE.Texture {
  const size = 512;
  return makeTexture(`stitch_${pattern}_${color}`, size, (ctx) => {
    ctx.clearRect(0, 0, size, size);
    ctx.strokeStyle = color;
    ctx.lineCap = 'round';
    const dash = (lw: number) => { ctx.lineWidth = lw; ctx.setLineDash([lw * 2.2, lw * 1.6]); };
    const line = (x0: number, y0: number, x1: number, y1: number) => { ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke(); };
    dash(3);
    if (pattern === 'single') { line(0, size * 0.5, size, size * 0.5); }
    else if (pattern === 'double') { line(0, size * 0.47, size, size * 0.47); line(0, size * 0.53, size, size * 0.53); }
    else if (pattern === 'pleat') { for (let k = 0; k < 8; k++) line(0, (k + 0.5) * size / 8, size, (k + 0.5) * size / 8); }
    else if (pattern === 'diamond') {
      const n = 5; const s = size / n;
      for (let k = -n; k <= 2 * n; k++) { line(k * s, 0, k * s + size, size); line(k * s, size, k * s + size, 0); }
    } else if (pattern === 'hex') {
      const rr = size / 8; const h = rr * Math.sqrt(3);
      for (let row = -1; row < size / h + 2; row++) for (let col = -1; col < size / (rr * 1.5) + 2; col++) {
        const cx = col * rr * 1.5; const cy = row * h + (col % 2 ? h / 2 : 0);
        ctx.beginPath();
        for (let i = 0; i < 6; i++) { const a = Math.PI / 3 * i; const px = cx + rr * Math.cos(a), py = cy + rr * Math.sin(a); if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py); }
        ctx.closePath(); ctx.stroke();
      }
    }
  }, { color: true });
}

/** Instrument cluster face for a gauge theme (drawn once per theme/color). */
export function clusterTexture(theme: string, color: string, brightness: number): THREE.Texture {
  const w = 1024, h = 512;
  const key = `cluster_${theme}_${color}_${brightness.toFixed(2)}`;
  const hit = cache.get(key); if (hit) return hit;
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const ctx = c.getContext('2d')!;
  ctx.fillStyle = '#05060a'; ctx.fillRect(0, 0, w, h);
  const glow = (x: number, y: number, r: number, col: string) => { const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(x - r, y - r, 2 * r, 2 * r); };
  ctx.globalAlpha = 0.4 + 0.6 * brightness;
  const ticks = (cx: number, cy: number, r: number, n: number, a0: number, a1: number, major: number, col: string) => {
    for (let i = 0; i <= n; i++) {
      const a = a0 + (a1 - a0) * i / n; const big = i % major === 0;
      ctx.strokeStyle = col; ctx.lineWidth = big ? 4 : 2;
      ctx.beginPath(); ctx.moveTo(cx + Math.cos(a) * (r - (big ? 28 : 16)), cy + Math.sin(a) * (r - (big ? 28 : 16))); ctx.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r); ctx.stroke();
    }
  };
  const needle = (cx: number, cy: number, r: number, a: number, col: string) => { ctx.strokeStyle = col; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(cx - Math.cos(a) * 18, cy - Math.sin(a) * 18); ctx.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r); ctx.stroke(); ctx.fillStyle = '#222'; ctx.beginPath(); ctx.arc(cx, cy, 14, 0, Math.PI * 2); ctx.fill(); };
  const label = (t: string, x: number, y: number, s: number, col = '#e8e8ec', align: CanvasTextAlign = 'center') => { ctx.fillStyle = col; ctx.font = `${s}px "Segoe UI", Roboto, Helvetica, Arial, sans-serif`; ctx.textAlign = align; ctx.fillText(t, x, y); };
  // analog speedometer (left): 0-200 mph
  const sx = 170, sy = 256, sr = 150;
  ctx.strokeStyle = '#2a2d36'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(sx, sy, sr + 6, 0, Math.PI * 2); ctx.stroke();
  ticks(sx, sy, sr, 40, Math.PI * 0.75, Math.PI * 2.25, 4, '#d0d2d8');
  for (let i = 0; i <= 10; i++) { const a = Math.PI * 0.75 + (Math.PI * 1.5) * i / 10; label(String(i * 20), sx + Math.cos(a) * (sr - 52), sy + Math.sin(a) * (sr - 52) + 8, 22); }
  label('MPH', sx, sy + 70, 18, '#9a9ca4');
  needle(sx, sy, sr - 20, Math.PI * 0.75 + 0.02, color);
  // centre 8-inch display area
  const cx = 512, cy = 256;
  ctx.fillStyle = '#070a12'; ctx.fillRect(cx - 230, cy - 140, 460, 280);
  if (theme === 'sport' || theme === 'concept_neon') {
    glow(cx, cy, 190, theme === 'concept_neon' ? color + '55' : '#2a0a0a88');
    ticks(cx, cy, 180, 32, Math.PI * 0.75, Math.PI * 2.25, 4, '#e8e8ec');
    for (let i = 0; i <= 8; i++) { const a = Math.PI * 0.75 + (Math.PI * 1.5) * i / 8; label(String(i), cx + Math.cos(a) * 140, cy + Math.sin(a) * 140 + 10, 26); }
    ctx.strokeStyle = color; ctx.lineWidth = 10; ctx.beginPath(); ctx.arc(cx, cy, 196, Math.PI * 1.85, Math.PI * 2.25); ctx.stroke();
    needle(cx, cy, 150, Math.PI * 0.75 + 0.25, color);
    label('42', cx, cy + 20, 64, '#ffffff'); label('MPH', cx, cy + 48, 18, '#9a9ca4');
    label('D', cx + 150, cy + 110, 36, color);
  } else if (theme === 'track') {
    // hockey-stick tach along the top with shift lights and large gear indicator
    ctx.fillStyle = '#101320'; ctx.fillRect(cx - 220, cy - 128, 440, 46);
    for (let i = 0; i < 20; i++) { ctx.fillStyle = i < 7 ? color : '#2a2d36'; ctx.fillRect(cx - 212 + i * 22, cy - 120, 18, 30); }
    ctx.strokeStyle = '#e8e8ec'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(cx - 220, cy - 60); ctx.lineTo(cx + 60, cy - 60); ctx.lineTo(cx + 220, cy - 100); ctx.stroke();
    for (let i = 0; i <= 7; i++) label(String(i), cx - 210 + i * 56, cy - 36, 20);
    label('3', cx, cy + 70, 120, '#ffffff'); label('GEAR', cx, cy + 110, 18, '#9a9ca4');
    label('42 MPH', cx - 160, cy + 100, 28); label('OIL 210°', cx + 160, cy + 100, 20, '#9a9ca4');
  } else if (theme === 'concept_minimal') {
    label('42', cx, cy + 24, 110, '#ffffff'); label('mph', cx, cy + 60, 22, '#9a9ca4');
    ctx.strokeStyle = color; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(cx - 200, cy + 100); ctx.lineTo(cx - 200 + 400 * 0.3, cy + 100); ctx.stroke();
    ctx.strokeStyle = '#2a2d36'; ctx.beginPath(); ctx.moveTo(cx - 200 + 400 * 0.3, cy + 100); ctx.lineTo(cx + 200, cy + 100); ctx.stroke();
    label('CONCEPT THEME', cx, cy - 100, 16, '#6a6c74');
  } else {
    // tour: modern layout with an arc tach, digital speed and infotainment info
    ctx.strokeStyle = '#2a2d36'; ctx.lineWidth = 14; ctx.beginPath(); ctx.arc(cx, cy + 20, 150, Math.PI * 0.8, Math.PI * 2.2); ctx.stroke();
    ctx.strokeStyle = color; ctx.beginPath(); ctx.arc(cx, cy + 20, 150, Math.PI * 0.8, Math.PI * 1.15); ctx.stroke();
    for (let i = 0; i <= 7; i++) { const a = Math.PI * 0.8 + (Math.PI * 1.4) * i / 7; label(String(i), cx + Math.cos(a) * 120, cy + 20 + Math.sin(a) * 120 + 8, 20, '#c0c2c8'); }
    label('42', cx, cy + 40, 72, '#ffffff'); label('MPH', cx, cy + 70, 18, '#9a9ca4');
    label('D', cx + 165, cy + 125, 28, '#e8e8ec'); label('TOUR', cx - 165, cy + 125, 18, '#9a9ca4');
    label('72°F  •  245 mi range', cx, cy - 110, 18, '#9a9ca4');
  }
  // fuel and temp (right)
  const gx = 880; 
  ticks(gx, 160, 60, 8, Math.PI * 0.75, Math.PI * 1.75, 4, '#d0d2d8'); label('F', gx + 40, 120, 18); label('E', gx - 60, 200, 18); needle(gx, 160, 48, Math.PI * 1.0, color);
  ticks(gx, 360, 60, 8, Math.PI * 0.75, Math.PI * 1.75, 4, '#d0d2d8'); label('H', gx + 40, 320, 18); label('C', gx - 60, 400, 18); needle(gx, 360, 48, Math.PI * 1.25, color);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.flipY = false;
  cache.set(key, t);
  return t;
}

/** Infotainment screen texture. */
export function infotainmentTexture(theme: string, brightness: number): THREE.Texture {
  const w = 512, h = 320;
  const key = `info_${theme}_${brightness.toFixed(2)}`;
  const hit = cache.get(key); if (hit) return hit;
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const ctx = c.getContext('2d')!;
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.flipY = false; cache.set(key, t);
  const alpha = 0.5 + 0.5 * brightness;
  if (theme === 'factory') {
    // factory screen: crossed flags with the CORVETTE wordmark under them on black, temperature and clock in the strip
    ctx.fillStyle = '#000000'; ctx.fillRect(0, 0, w, h);
    ctx.globalAlpha = alpha;
    ctx.fillStyle = '#e8e9ec'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.font = 'bold 44px "Arial Black", "Segoe UI", Roboto, Helvetica, Arial, sans-serif';
    const text = 'CORVETTE', spacing = 10;
    let total = -spacing; for (const ch of text) total += ctx.measureText(ch).width + spacing;
    let x = (w - total) / 2;
    for (const ch of text) { const cw = ctx.measureText(ch).width; ctx.fillText(ch, x + cw / 2, h * 0.78); x += cw + spacing; }
    ctx.textBaseline = 'alphabetic';
    const img = new Image();
    img.onload = () => {
      const lw = w * 0.44, lh = lw * (img.height / img.width);
      ctx.globalAlpha = alpha;
      ctx.drawImage(img, (w - lw) / 2, h * 0.46 - lh / 2, lw, lh);
      t.needsUpdate = true;
      (t as unknown as THREE.EventDispatcher<{ imageLoaded: object }>).dispatchEvent({ type: 'imageLoaded' });
    };
    img.src = `${import.meta.env.BASE_URL}branding/crossed-flags.png`;
    t.needsUpdate = true;
    return t;
  }
  const accent = theme === 'concept_red' ? '#ff3b30' : theme === 'concept_blue' ? '#3d7bff' : '#9aa0a6';
  ctx.fillStyle = '#06070a'; ctx.fillRect(0, 0, w, h);
  ctx.globalAlpha = alpha;
  ctx.fillStyle = accent; ctx.fillRect(0, 0, w, 6);
  ctx.fillStyle = '#e8e8ec'; ctx.font = '26px "Segoe UI", Roboto, Helvetica, Arial, sans-serif'; ctx.textAlign = 'left';
  ctx.fillText('Studio Concept UI', 24, 48);
  const tiles = ['Audio', 'Phone', 'Nav', 'PDR', 'Settings', 'Climate'];
  tiles.forEach((tl, i) => { const x = 24 + (i % 3) * 156, y = 80 + Math.floor(i / 3) * 110; ctx.fillStyle = '#14161c'; ctx.fillRect(x, y, 140, 90); ctx.fillStyle = accent; ctx.fillRect(x, y + 82, 140, 4); ctx.fillStyle = '#e8e8ec'; ctx.font = '20px sans-serif'; ctx.fillText(tl, x + 14, y + 36); });
  ctx.fillStyle = '#9aa0a6'; ctx.font = '16px sans-serif'; ctx.textAlign = 'right'; ctx.fillText('CONCEPT (non-factory)', w - 16, h - 14);
  t.needsUpdate = true;
  return t;
}

/** Text label texture (headrest embroidery, floor mats, sill plates). */
export function textTexture(text: string, color: string, bg = 'rgba(0,0,0,0)'): THREE.Texture {
  const w = 512, h = 128;
  const key = `text_${text}_${color}_${bg}`;
  const hit = cache.get(key); if (hit) return hit;
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const ctx = c.getContext('2d')!;
  ctx.fillStyle = bg; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = color; ctx.font = 'bold 64px "Segoe UI", Roboto, Helvetica, Arial, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(text.slice(0, 16), w / 2, h / 2);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; cache.set(key, t); return t;
}

let emblemTex: THREE.Texture | null = null;
/** Crossed-flags artwork supplied by the owner (public/branding/crossed-flags.png). */
export function emblemTexture(): THREE.Texture {
  if (emblemTex) return emblemTex;
  const t = new THREE.TextureLoader().load(`${import.meta.env.BASE_URL}branding/crossed-flags.png`);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  emblemTex = t;
  return t;
}

export function disposeTextureCache() { for (const t of cache.values()) t.dispose(); cache.clear(); }
