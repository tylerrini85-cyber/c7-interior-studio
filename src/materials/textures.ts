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
  // Canvas covers the cluster dial plane: 0.380 x 0.170 m at 3000 px/m. u (m, right) and v (m, up) are measured
  // from the cluster centre exactly as in tools/blender/parts/dashboard.py (CL_* constants), from B41 / B21 / B13.
  const w = 1140, h = 510;
  const key = `cluster2_${theme}_${color}_${brightness.toFixed(2)}`;
  const hit = cache.get(key); if (hit) return hit;
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const ctx = c.getContext('2d')!;
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.flipY = false; cache.set(key, t);
  const P = (u: number, v: number): [number, number] => [(u + 0.190) * 3000, (0.080 - v) * 3000];
  const D = Math.PI / 180;
  const font = (px: number, weight = 'bold', italic = true) => `${italic ? 'italic ' : ''}${weight} ${px}px "Segoe UI", Roboto, Helvetica, Arial, sans-serif`;
  const text = (s: string, x: number, y: number, px: number, col = '#f2f3f5', align: CanvasTextAlign = 'center', weight = 'bold', italic = true) => {
    ctx.font = font(px, weight, italic); ctx.fillStyle = col; ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.fillText(s, x, y);
  };
  const glowOn = (col: string, blur: number) => { ctx.shadowColor = col; ctx.shadowBlur = blur; };
  const glowOff = () => { ctx.shadowBlur = 0; };
  const NEEDLE = '#ff4a1c';
  ctx.fillStyle = '#000000'; ctx.fillRect(0, 0, w, h);
  ctx.globalAlpha = 0.45 + 0.55 * brightness;

  // ---- left pod: speedometer 0-200 mph; arc runs from straight down (0) round the outer side to up-right (200)
  {
    const [px, py] = P(-0.128, -0.017);
    const R = 150, ang = (mph: number) => (88 + (mph / 200) * 200) * D;
    glowOn('rgba(255,255,255,0.55)', 6);
    for (let mph = 0; mph <= 200; mph += 5) {
      const a = ang(mph), major = mph % 20 === 0, mid = mph % 10 === 0;
      const r0 = R - (major ? 26 : mid ? 18 : 12);
      ctx.strokeStyle = '#f4f5f7'; ctx.lineWidth = major ? 5 : 3;
      ctx.beginPath(); ctx.moveTo(px + Math.cos(a) * r0, py + Math.sin(a) * r0); ctx.lineTo(px + Math.cos(a) * R, py + Math.sin(a) * R); ctx.stroke();
      if (major && mph > 0) { const rn = R - 46; text(String(mph), px + Math.cos(a) * rn, py + Math.sin(a) * rn, 21); }
    }
    text('0', px + Math.cos(ang(0)) * (R - 46) + 6, py + Math.sin(ang(0)) * (R - 46), 21);
    text('MPH', px - 32, py + 58, 22);
    glowOff();
    // needle at rest (0 mph), physical orange-red pointer
    glowOn(NEEDLE, 14); ctx.strokeStyle = NEEDLE; ctx.lineWidth = 7; ctx.lineCap = 'round';
    const a0 = ang(0); ctx.beginPath(); ctx.moveTo(px - Math.cos(a0) * 10, py - Math.sin(a0) * 10); ctx.lineTo(px + Math.cos(a0) * (R - 6), py + Math.sin(a0) * (R - 6)); ctx.stroke(); glowOff();
  }

  // ---- right pod: fuel (upper arc, 1 at the top to 0 at the right) and coolant (lower arc, 260 down to 100 °F)
  {
    const [px, py] = P(0.128, -0.012);
    const R = 143;
    const arcTicks = (a0: number, a1: number, n: number, redFrom: number | null) => {
      for (let i = 0; i <= n; i++) {
        const a = (a0 + (a1 - a0) * i / n) * D, major = i % 2 === 0;
        const red = redFrom !== null && i >= redFrom;
        ctx.strokeStyle = red ? '#ff3b1f' : '#f4f5f7'; ctx.lineWidth = major ? 5 : 3;
        const r0 = R - (major ? 24 : 14);
        ctx.beginPath(); ctx.moveTo(px + Math.cos(a) * r0, py + Math.sin(a) * r0); ctx.lineTo(px + Math.cos(a) * R, py + Math.sin(a) * R); ctx.stroke();
      }
    };
    glowOn('rgba(255,255,255,0.5)', 6);
    arcTicks(-110, -15, 8, 7);
    const lab = (s: string, deg: number, r = R - 44, px2 = 21) => text(s, px + Math.cos(deg * D) * r, py + Math.sin(deg * D) * r, px2);
    lab('1', -110); lab('½', -62); lab('0', -15);
    arcTicks(19, 97, 8, null);
    ctx.strokeStyle = '#ff3b1f'; ctx.lineWidth = 5; ctx.beginPath(); ctx.arc(px, py, R - 4, 12 * D, 22 * D); ctx.stroke();
    lab('260', 22, R - 50, 19); lab('220', 57, R - 48, 19); lab('100', 97, R - 44, 19);
    text('CORVETTE', px + 86, py + 3, 16, '#f4f5f7', 'center', 'bold', true);
    // fuel pump and thermometer glyphs
    ctx.strokeStyle = '#f4f5f7'; ctx.lineWidth = 3;
    { const gx = px + 78, gy = py - 72; ctx.strokeRect(gx - 7, gy - 10, 12, 18); ctx.beginPath(); ctx.moveTo(gx + 5, gy - 6); ctx.lineTo(gx + 10, gy - 2); ctx.lineTo(gx + 10, gy + 8); ctx.stroke(); }
    { const gx = px + 100, gy = py + 58; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(gx, gy - 9); ctx.lineTo(gx, gy + 3); ctx.stroke(); ctx.beginPath(); ctx.arc(gx, gy + 6, 4, 0, Math.PI * 2); ctx.stroke(); ctx.beginPath(); ctx.moveTo(gx - 7, gy + 12); ctx.quadraticCurveTo(gx, gy + 9, gx + 7, gy + 12); ctx.stroke(); ctx.lineWidth = 3; }
    glowOff();
    glowOn(NEEDLE, 14); ctx.strokeStyle = NEEDLE; ctx.lineWidth = 7; ctx.lineCap = 'round';
    for (const deg of [-57, 90]) { const a = deg * D; ctx.beginPath(); ctx.moveTo(px - Math.cos(a) * 8, py - Math.sin(a) * 8); ctx.lineTo(px + Math.cos(a) * (R - 8), py + Math.sin(a) * (R - 8)); ctx.stroke(); }
    glowOff();
  }

  // ---- centre 8-inch display (clipped to its opening)
  const [dx0, dy0] = P(-0.089, 0.067), [dx1, dy1] = P(0.089, -0.043);
  const dcx = (dx0 + dx1) / 2, dcy = (dy0 + dy1) / 2, dw = dx1 - dx0, dh = dy1 - dy0;
  ctx.save(); ctx.beginPath(); ctx.rect(dx0, dy0, dw, dh); ctx.clip();
  const g = ctx.createLinearGradient(0, dy0, 0, dy1); g.addColorStop(0, '#0b0f18'); g.addColorStop(1, '#03050a');
  ctx.fillStyle = g; ctx.fillRect(dx0, dy0, dw, dh);
  if (theme === 'track') {
    // Track (B41): shift-light dots, rising tach band, performance timers, gauge bars, tyre pressures
    for (let i = 0; i < 11; i++) { ctx.fillStyle = '#2b3240'; ctx.beginPath(); ctx.arc(dcx - 105 + i * 21, dy0 + 22, 6, 0, Math.PI * 2); ctx.fill(); }
    const bx0 = dx0 + 40, bx1 = dx1 - 20, by0 = dy0 + 220, by1 = dy0 + 60;
    const curve = (k: number) => [bx0 + (bx1 - bx0) * k, by0 - (by0 - by1) * Math.pow(k, 0.45)] as [number, number];
    for (let i = 0; i < 14; i++) {
      const k0 = i / 14, k1 = (i + 1) / 14; const [x0, y0] = curve(k0), [x1, y1] = curve(k1);
      ctx.fillStyle = k0 >= 0.86 ? '#ff4a4a' : '#202a44';
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.lineTo(x1, by0 + 8); ctx.lineTo(x0, by0 + 8); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = '#3a4466'; ctx.lineWidth = 1; ctx.stroke();
    }
    ctx.strokeStyle = '#ff6a3a'; ctx.lineWidth = 3; ctx.beginPath(); for (let i = 0; i <= 40; i++) { const [x, y] = curve(i / 40); if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y); } ctx.stroke();
    for (let n = 1; n <= 7; n++) { const [x, y] = curve(n / 7.6); text(String(n), x, y + 24, 22); }
    text('Best', dx0 + 52, dy0 + 120, 13, '#f0c040'); text('0:00.0', dx0 + 52, dy0 + 136, 15, '#e8e8ec');
    text('Previous', dx0 + 112, dy0 + 82, 13, '#f0c040'); text('0:00.0', dx0 + 112, dy0 + 98, 15, '#e8e8ec');
    text('Current', dx0 + 182, dy0 + 54, 13, '#f0c040'); text('0:00.0', dx0 + 182, dy0 + 70, 15, '#e8e8ec');
    ctx.strokeStyle = '#d8dbe0'; ctx.lineWidth = 2; ctx.strokeRect(dcx - 50, dy0 + 150, 100, 22); text('COOL', dcx, dy0 + 161, 15, '#f2f3f5', 'center', 'bold', false);
    for (const [k, x] of [[0, dcx - 150], [1, dcx - 118], [2, dcx + 118], [3, dcx + 150]] as [number, number][]) { ctx.strokeStyle = '#b8bcc4'; ctx.strokeRect(x - 7, dy0 + 186, 14, 60); ctx.fillStyle = k === 3 ? '#e8e8ec' : '#f0c040'; ctx.fillRect(x - 5, dy0 + 216, 10, 28); }
    ctx.fillStyle = '#e8e8ec'; ctx.beginPath(); ctx.ellipse(dcx, dy0 + 222, 13, 30, 0, 0, Math.PI * 2); ctx.fill();
    for (const [x, y] of [[dcx - 46, dy0 + 196], [dcx + 46, dy0 + 196], [dcx - 46, dy0 + 238], [dcx + 46, dy0 + 238]]) { ctx.strokeStyle = '#d8dbe0'; ctx.strokeRect(x - 20, y - 11, 40, 22); text('32', x, y, 15, '#f2f3f5', 'center', 'bold', false); }
    text('0', dx0 + 128, dy1 - 52, 46); text('MPH', dx0 + 170, dy1 - 46, 13);
    text('412 mi', dx0 + 52, dy1 - 22, 16, '#e8e8ec', 'center', 'normal', false);
    text('PARK', dcx + 44, dy1 - 22, 14, '#ff7a2a'); text('SW', dx1 - 28, dy1 - 22, 16, '#e8e8ec');
  } else if (theme === 'sport') {
    // Sport: tach as a wide arc across the top, big digital speed, gear in the centre
    const cx0 = dcx, cy0 = dcy + 70, R = 190;
    ctx.lineWidth = 16; ctx.strokeStyle = '#1c2230'; ctx.beginPath(); ctx.arc(cx0, cy0, R, 200 * D, 340 * D); ctx.stroke();
    ctx.strokeStyle = color; ctx.beginPath(); ctx.arc(cx0, cy0, R, 200 * D, 230 * D); ctx.stroke();
    ctx.strokeStyle = '#ff3b1f'; ctx.beginPath(); ctx.arc(cx0, cy0, R, 322 * D, 340 * D); ctx.stroke();
    for (let n = 0; n <= 7; n++) { const a = (200 + n * 20) * D; text(String(n), cx0 + Math.cos(a) * (R - 34), cy0 + Math.sin(a) * (R - 34), 22); }
    text('0', cx0, cy0 - 70, 70); text('MPH', cx0, cy0 - 26, 16, '#9aa0aa');
    ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.strokeRect(cx0 - 22, cy0 + 4, 44, 44); text('P', cx0, cy0 + 27, 32, color);
    text('SPORT', dx0 + 50, dy1 - 20, 14, '#9aa0aa'); text('412 mi', dx1 - 52, dy1 - 20, 14, '#9aa0aa', 'center', 'normal', false);
  } else if (theme === 'concept_neon') {
    const cx0 = dcx, cy0 = dcy;
    const gg = ctx.createRadialGradient(cx0, cy0, 0, cx0, cy0, 170); gg.addColorStop(0, color + '55'); gg.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = gg; ctx.fillRect(dx0, dy0, dw, dh);
    glowOn(color, 18); ctx.strokeStyle = color; ctx.lineWidth = 8; ctx.beginPath(); ctx.arc(cx0, cy0, 140, 135 * D, 405 * D); ctx.stroke(); glowOff();
    text('0', cx0, cy0, 80); text('MPH', cx0, cy0 + 46, 16, '#9aa0aa'); text('CONCEPT', cx0, dy1 - 18, 12, '#6a6c74', 'center', 'normal', false);
  } else if (theme === 'concept_minimal') {
    text('0', dcx, dcy - 6, 110, '#ffffff', 'center', '300', false); text('mph', dcx, dcy + 60, 20, '#9aa0aa', 'center', 'normal', false);
    ctx.strokeStyle = '#2a2d36'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(dcx - 200, dy1 - 40); ctx.lineTo(dcx + 200, dy1 - 40); ctx.stroke();
    ctx.strokeStyle = color; ctx.beginPath(); ctx.moveTo(dcx - 200, dy1 - 40); ctx.lineTo(dcx - 140, dy1 - 40); ctx.stroke();
    text('CONCEPT', dcx, dy0 + 22, 12, '#6a6c74', 'center', 'normal', false);
  } else {
    // Tour (factory default, B21 / B13): round tachometer with a bright ring, numerals 0-7, redline, crossed flags
    const cx0 = dcx, cy0 = dcy + 4, R = 152;
    const ring = ctx.createLinearGradient(cx0 - R, cy0 - R, cx0 + R, cy0 + R); ring.addColorStop(0, '#dfe8f4'); ring.addColorStop(0.5, '#7d8da6'); ring.addColorStop(1, '#e8eef6');
    ctx.strokeStyle = ring; ctx.lineWidth = 8; ctx.beginPath(); ctx.arc(cx0, cy0, R, 0, Math.PI * 2); ctx.stroke();
    const tang = (k: number) => (128 + k * 35.3) * D;
    ctx.strokeStyle = '#ff2a1a'; ctx.lineWidth = 10; ctx.beginPath(); ctx.arc(cx0, cy0, R - 12, tang(6.3), tang(8)); ctx.stroke();
    glowOn('rgba(255,255,255,0.5)', 5);
    for (let i = 0; i <= 28; i++) { const k = i / 4, a = tang(k), major = i % 4 === 0; ctx.strokeStyle = k >= 6.5 ? '#ff4030' : '#f2f3f5'; ctx.lineWidth = major ? 5 : 2; const r0 = R - (major ? 34 : 24); ctx.beginPath(); ctx.moveTo(cx0 + Math.cos(a) * r0, cy0 + Math.sin(a) * r0); ctx.lineTo(cx0 + Math.cos(a) * (R - 16), cy0 + Math.sin(a) * (R - 16)); ctx.stroke(); }
    for (let k = 0; k <= 7; k++) { const a = tang(k); text(String(k), cx0 + Math.cos(a) * (R - 60), cy0 + Math.sin(a) * (R - 60), 34); }
    text('RPM x1000', cx0 - 70, cy0 + 70, 11, '#c8ccd2', 'center', 'normal', false);
    glowOff();
    // gear indicator and digital speed
    ctx.strokeStyle = '#e8eef6'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(cx0 + 92, cy0 + 96, 20, 0, Math.PI * 2); ctx.stroke(); text('P', cx0 + 92, cy0 + 97, 26, '#ffffff');
    text('0 MPH', cx0, cy0 + 112, 15, '#f0c040', 'center', 'bold', false);
    // side scales (oil pressure left, oil temperature right)
    for (const sx of [-1, 1]) { ctx.strokeStyle = '#c8ccd2'; ctx.lineWidth = 2; const ax = cx0 + sx * 228; ctx.beginPath(); ctx.arc(ax - sx * 40, cy0, 70, sx < 0 ? 150 * D : -30 * D, sx < 0 ? 210 * D : 30 * D); ctx.stroke(); for (let i = 0; i <= 4; i++) { const a = (sx < 0 ? 150 + i * 15 : -30 + i * 15) * D; ctx.beginPath(); ctx.moveTo(ax - sx * 40 + Math.cos(a) * 62, cy0 + Math.sin(a) * 62); ctx.lineTo(ax - sx * 40 + Math.cos(a) * 70, cy0 + Math.sin(a) * 70); ctx.stroke(); } }
    // needle at idle
    glowOn('#ff3010', 12); ctx.strokeStyle = '#ff3a1a'; ctx.lineWidth = 6; ctx.lineCap = 'round'; const na = tang(0.8); ctx.beginPath(); ctx.moveTo(cx0 - Math.cos(na) * 20, cy0 - Math.sin(na) * 20); ctx.lineTo(cx0 + Math.cos(na) * (R - 22), cy0 + Math.sin(na) * (R - 22)); ctx.stroke(); glowOff();
    ctx.fillStyle = '#111317'; ctx.beginPath(); ctx.arc(cx0, cy0, 14, 0, Math.PI * 2); ctx.fill();
    // crossed flags at the top of the dial
    const img = new Image();
    img.onload = () => {
      ctx.save(); ctx.beginPath(); ctx.rect(dx0, dy0, dw, dh); ctx.clip(); ctx.globalAlpha = 0.45 + 0.55 * brightness;
      const lw = 64, lh = lw * (img.height / img.width); ctx.drawImage(img, cx0 - lw / 2, cy0 - 78 - lh / 2, lw, lh); ctx.restore();
      t.needsUpdate = true; (t as unknown as THREE.EventDispatcher<{ imageLoaded: object }>).dispatchEvent({ type: 'imageLoaded' });
    };
    img.src = `${import.meta.env.BASE_URL}branding/crossed-flags.png`;
  }
  ctx.restore();
  t.needsUpdate = true;
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


let panelTex: THREE.Texture | null = null;
/** Transparent overlay for the centre-stack control panel: key outlines, icons and labels laid out from the
 *  reference photo. Panel is 310 x 122 mm; the texture is 1240 x 488 px (4 px per mm). Centre of the panel is
 *  at stack height 0.628; the knob openings are left clear at x = +-128 mm. */
export function controlPanelTexture(): THREE.Texture {
  if (panelTex) return panelTex;
  const w = 1240, h = 488, ppm = 4;
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const ctx = c.getContext('2d')!;
  ctx.clearRect(0, 0, w, h);
  const X = (mm: number) => w / 2 + mm * ppm;              // mm from the panel centre, right positive
  const Y = (zmm: number) => h / 2 - (zmm - 628) * ppm;     // stack height in mm -> canvas row
  const key = (x: number, y: number, wmm: number, hmm: number, label: string, glyph?: (cx: number, cy: number) => void) => {
    const kw = wmm * ppm, kh = hmm * ppm, r = 6;
    ctx.beginPath(); ctx.roundRect(x - kw / 2, y - kh / 2, kw, kh, r);
    ctx.fillStyle = 'rgba(28,28,31,0.96)'; ctx.fill();
    ctx.strokeStyle = 'rgba(80,80,86,0.9)'; ctx.lineWidth = 2; ctx.stroke();
    ctx.fillStyle = '#e6e8ea'; ctx.strokeStyle = '#e6e8ea';
    if (glyph) { glyph(x, y - (label ? 7 : 0)); }
    if (label) { ctx.font = `${glyph ? 'bold 15px' : 'bold 19px'} "Segoe UI", Roboto, Helvetica, Arial, sans-serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(label, x, y + (glyph ? 18 : 0)); }
  };
  const person = (cx: number, cy: number, arrows: 'face' | 'both' | 'feet') => {
    ctx.lineWidth = 3; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.arc(cx - 10, cy - 12, 6, 0, Math.PI * 2); ctx.stroke();           // head
    ctx.beginPath(); ctx.moveTo(cx - 10, cy - 6); ctx.lineTo(cx - 10, cy + 8); ctx.lineTo(cx - 2, cy + 16); ctx.stroke(); // body / thigh
    const arrow = (y: number) => { ctx.beginPath(); ctx.moveTo(cx + 2, y); ctx.lineTo(cx + 16, y); ctx.moveTo(cx + 10, y - 5); ctx.lineTo(cx + 16, y); ctx.lineTo(cx + 10, y + 5); ctx.stroke(); };
    if (arrows !== 'feet') arrow(cy - 12);
    if (arrows !== 'face') arrow(cy + 14);
  };
  const defrost = (cx: number, cy: number, rear: boolean) => {
    ctx.lineWidth = 3; ctx.lineCap = 'round';
    ctx.beginPath();
    if (rear) ctx.roundRect(cx - 16, cy - 12, 32, 24, 4); else { ctx.moveTo(cx - 18, cy + 12); ctx.quadraticCurveTo(cx - 14, cy - 12, cx + 2, cy - 12); ctx.lineTo(cx + 18, cy - 12); }
    ctx.stroke();
    for (let i = -1; i <= 1; i++) { ctx.beginPath(); ctx.moveTo(cx + i * 9, cy + 8); ctx.quadraticCurveTo(cx + i * 9 + 4, cy, cx + i * 9, cy - 8); ctx.stroke(); }
  };
  const tri = (cx: number, cy: number, dir: 1 | -1, bar: boolean) => {
    ctx.beginPath(); ctx.moveTo(cx - 6 * dir, cy - 8); ctx.lineTo(cx + 6 * dir, cy); ctx.lineTo(cx - 6 * dir, cy + 8); ctx.closePath(); ctx.fill();
    if (bar) ctx.fillRect(cx + 7 * dir - 1, cy - 8, 2, 16);
  };
  // media row (z 666 mm): RADIO MEDIA home MENU prev next BACK at 26 mm pitch from -78 mm
  const zm = 666;
  const mx = (i: number) => X(-78 + 26 * i);  // RADIO MEDIA home (MENU) prev next BACK
  key(mx(0), Y(zm), 22, 13, 'RADIO');
  key(mx(1), Y(zm), 22, 13, 'MEDIA');
  key(mx(2), Y(zm), 22, 13, '', (cx, cy) => { ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(cx - 12, cy + 2); ctx.lineTo(cx, cy - 9); ctx.lineTo(cx + 12, cy + 2); ctx.moveTo(cx - 8, cy); ctx.lineTo(cx - 8, cy + 10); ctx.lineTo(cx + 8, cy + 10); ctx.lineTo(cx + 8, cy); ctx.stroke(); });
  // round MENU in the middle
  { const cx = mx(3), cy = Y(zm); ctx.beginPath(); ctx.arc(cx, cy, 12 * ppm, 0, Math.PI * 2); ctx.fillStyle = 'rgba(24,24,27,0.97)'; ctx.fill(); ctx.strokeStyle = 'rgba(120,120,128,0.9)'; ctx.lineWidth = 3; ctx.stroke(); ctx.fillStyle = '#e6e8ea'; ctx.font = 'bold 15px "Segoe UI", Roboto, Helvetica, Arial, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('MENU', cx, cy); }
  key(mx(4), Y(zm), 22, 13, '', (cx, cy) => { tri(cx - 4, cy + 7, -1, true); tri(cx + 8, cy + 7, -1, false); });
  key(mx(5), Y(zm), 22, 13, '', (cx, cy) => { tri(cx - 8, cy + 7, 1, false); tri(cx + 4, cy + 7, 1, true); });
  key(mx(6), Y(zm), 22, 13, 'BACK');
  // climate block (B58 / B21): two rows of six split down the middle by a chrome Y
  //   row A (z 636): AUTO  A/C  face   |  face+feet  front-defrost  SYNC
  //   row B (z 613): seat  feet  feet+defrost  |  rear-defrost  recirc  seat
  const cx = (i: number) => X(i < 3 ? -79 + 26 * i : 27 + 26 * (i - 3));
  const seat = (cx0: number, cy0: number) => { ctx.lineWidth = 3; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(cx0 - 9, cy0 - 12); ctx.lineTo(cx0 - 6, cy0 + 6); ctx.lineTo(cx0 + 10, cy0 + 6); ctx.stroke(); for (let k = 0; k < 3; k++) { ctx.beginPath(); ctx.moveTo(cx0 - 2 + k * 5, cy0 - 2); ctx.quadraticCurveTo(cx0 + 1 + k * 5, cy0 - 8, cx0 - 2 + k * 5, cy0 - 14); ctx.stroke(); } };
  const recirc = (cx0: number, cy0: number) => { ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(cx0 - 16, cy0 + 8); ctx.lineTo(cx0 + 14, cy0 + 8); ctx.stroke(); ctx.beginPath(); ctx.arc(cx0, cy0 - 1, 9, Math.PI * 0.1, Math.PI * 1.25, true); ctx.stroke(); ctx.beginPath(); ctx.moveTo(cx0 - 11, cy0 - 1); ctx.lineTo(cx0 - 6, cy0 + 4); ctx.lineTo(cx0 - 2, cy0 - 2); ctx.stroke(); };
  const za = 636, zb = 613;
  key(cx(0), Y(za), 22, 14, 'AUTO');
  key(cx(1), Y(za), 22, 14, 'A/C');
  key(cx(2), Y(za), 22, 14, '', (x0, y0) => person(x0, y0 + 7, 'face'));
  key(cx(3), Y(za), 22, 14, '', (x0, y0) => person(x0, y0 + 7, 'both'));
  key(cx(4), Y(za), 22, 14, '', (x0, y0) => defrost(x0, y0 + 7, false));
  key(cx(5), Y(za), 22, 14, 'SYNC');
  key(cx(0), Y(zb), 22, 14, '', (x0, y0) => seat(x0, y0 + 7));
  key(cx(1), Y(zb), 22, 14, '', (x0, y0) => person(x0, y0 + 7, 'feet'));
  key(cx(2), Y(zb), 22, 14, '', (x0, y0) => { person(x0 - 6, y0 + 7, 'feet'); defrost(x0 + 12, y0 + 7, false); });
  key(cx(3), Y(zb), 22, 14, '', (x0, y0) => defrost(x0, y0 + 7, true));
  key(cx(4), Y(zb), 22, 14, '', (x0, y0) => recirc(x0, y0 + 7));
  key(cx(5), Y(zb), 22, 14, '', (x0, y0) => seat(x0, y0 + 7));
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.needsUpdate = true;  // default flipY: upright on a PlaneGeometry
  panelTex = t;
  return t;
}

const knobTex: Record<string, THREE.Texture> = {};
/** Climate knob faces (B58): temperature knob shows "LO" inside a blue-to-red ring, fan knob shows the fan symbol. */
export function knobFaceTexture(kind: 'temp' | 'fan'): THREE.Texture {
  if (knobTex[kind]) return knobTex[kind];
  const n = 256; const c = document.createElement('canvas'); c.width = n; c.height = n;
  const ctx = c.getContext('2d')!;
  ctx.clearRect(0, 0, n, n);
  const m = n / 2;
  ctx.fillStyle = '#0c0d10'; ctx.beginPath(); ctx.arc(m, m, m - 4, 0, Math.PI * 2); ctx.fill();
  if (kind === 'temp') {
    const g = ctx.createLinearGradient(0, n, n, 0); g.addColorStop(0, '#2f7bff'); g.addColorStop(1, '#ff3b30');
    ctx.strokeStyle = g; ctx.lineWidth = 10; ctx.beginPath(); ctx.arc(m, m, m - 26, Math.PI * 0.75, Math.PI * 2.25); ctx.stroke();
    ctx.fillStyle = '#f2f3f5'; ctx.font = 'bold 64px "Segoe UI", Roboto, Helvetica, Arial, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('LO', m, m + 4);
  } else {
    ctx.strokeStyle = '#c8ccd2'; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(m, m, m - 26, 0, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = '#f2f3f5';
    for (let i = 0; i < 4; i++) { ctx.save(); ctx.translate(m, m); ctx.rotate(i * Math.PI / 2 + 0.3); ctx.beginPath(); ctx.ellipse(0, -26, 13, 24, 0.5, 0, Math.PI * 2); ctx.fill(); ctx.restore(); }
    ctx.beginPath(); ctx.arc(m, m, 9, 0, Math.PI * 2); ctx.fill();
  }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.needsUpdate = true;
  knobTex[kind] = t; return t;
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
