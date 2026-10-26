/** Curated design presets and the themed random generator. Presets are real customization settings. */
import type { PartConfig, ProjectDoc, MaterialKind, ZoneId } from './schema';
import { COMPONENTS, factoryParts, VARIANTS } from '../registry/components';
import { defaultLighting } from './schema';

export interface Preset {
  id: string; name: string; description: string; apply: (doc: ProjectDoc) => void;
}


function setAll(doc: ProjectDoc, filter: (id: string) => boolean, patch: Partial<PartConfig>) {
  for (const c of COMPONENTS) {
    if (!filter(c.id)) continue;
    const cur = doc.parts[c.id];
    if (!cur) continue;
    const next = { ...cur, ...patch };
    if (patch.material && !c.caps.materials.includes(patch.material)) next.material = cur.material;
    if (patch.stitch && !c.caps.stitch) delete next.stitch;
    doc.parts[c.id] = next;
  }
}

function isSoft(id: string) { const c = COMPONENTS.find((x) => x.id === id); return !!c && c.caps.materials.includes('leather'); }
const TRIM_SEGMENTS = new Set(['trim', 'insert', 'vents', 'side_trim', 'speaker', 'handle', 'ring', 'emblem', 'spokes', 'sills', 'dial', 'paddles', 'grab_trim']);
function isTrim(id: string) { return id.split('.').some((seg) => TRIM_SEGMENTS.has(seg)); }
function isSeatInsert(id: string) { return /seats\..*\.center$/.test(id); }
function isSeat(id: string) { return id.startsWith('seats.'); }

function allZones(doc: ProjectDoc, color: string, brightness = 0.8) {
  doc.lighting.master = { ...doc.lighting.master, enabled: true, color, brightness, sync: true, mode: 'solid' };
  for (const z of Object.keys(doc.lighting.zones) as ZoneId[]) doc.lighting.zones[z] = { enabled: true, color, brightness };
}

export const PRESETS: Preset[] = [
  { id: 'factory', name: 'Factory Original', description: '2019 Stingray 3LT Jet Black Napa leather', apply: (doc) => { doc.parts = factoryParts(doc.base.factoryColor); doc.lighting = defaultLighting(); } },
  { id: 'stealth', name: 'Stealth Black', description: 'All-black leather and matte carbon with black stitching', apply: (doc) => {
    doc.parts = factoryParts('jet_black');
    setAll(doc, isSoft, { color: '#0d0d0f', stitch: { color: '#1c1c1e', pattern: 'single' } });
    setAll(doc, isTrim, { material: 'carbon_matte', color: '#111113' });
    setAll(doc, (id) => id === 'console.shifter.ring', { material: 'anodized', color: '#1a1a1c' });
  } },
  { id: 'redline', name: 'Redline Performance', description: 'Black Alcantara with Adrenaline Red inserts and red stitching', apply: (doc) => {
    doc.parts = factoryParts('jet_black');
    setAll(doc, isSoft, { material: 'alcantara', color: '#121214', stitch: { color: '#d2232a', pattern: 'single' } });
    setAll(doc, isSeatInsert, { material: 'leather_perforated', color: '#8f1a20', stitch: { color: '#d2232a', pattern: 'pleat' } });
    setAll(doc, (id) => id.startsWith('steering.rim.upper'), { material: 'alcantara', color: '#121214', variant: 'flat_bottom' });
    setAll(doc, isTrim, { material: 'carbon_gloss', color: '#141416' });
    doc.parts['dash.trim.driver'].material = 'anodized'; doc.parts['dash.trim.driver'].color = '#b3161c';
    doc.parts['dash.trim.passenger'].material = 'anodized'; doc.parts['dash.trim.passenger'].color = '#b3161c';
    allZones(doc, '#ff1e1e', 0.75);
  } },
  { id: 'carbon', name: 'Carbon Edition', description: 'Gloss twill carbon trim everywhere with gray stitching', apply: (doc) => {
    doc.parts = factoryParts('jet_black');
    setAll(doc, isTrim, { material: 'carbon_gloss', color: '#141416' });
    setAll(doc, (id) => ['dash.glovebox', 'console.stack', 'console.trim', 'roof.panel', 'steering.hub'].includes(id), { material: 'carbon_gloss', color: '#141416' });
    setAll(doc, isSoft, { stitch: { color: '#8a8a8e', pattern: 'single' } });
  } },
  { id: 'luxury_tan', name: 'Luxury Tan', description: 'Kalahari leather, diamond-stitched inserts, polished aluminum', apply: (doc) => {
    doc.parts = factoryParts('kalahari');
    setAll(doc, isSeatInsert, { material: 'leather', color: '#a98a62', stitch: { color: '#5a4630', pattern: 'diamond' } });
    setAll(doc, (id) => id === 'console.armrest' || id.endsWith('.armrest'), { stitch: { color: '#5a4630', pattern: 'diamond' } });
    setAll(doc, isTrim, { material: 'aluminum_polished', color: '#c9ccd2' });
    setAll(doc, (id) => id === 'roof.headliner' || id === 'roof.panel' || id === 'pillars' || id === 'roof.visors', { material: 'suede', color: '#6b5a44' });
    setAll(doc, (id) => id === 'floor.carpet' || id.startsWith('floor.mats'), { color: '#2a241c' });
  } },
  { id: 'midnight_blue', name: 'Midnight Blue', description: 'Deep navy leather with ice-blue stitching and blue ambient light', apply: (doc) => {
    doc.parts = factoryParts('jet_black');
    setAll(doc, isSoft, { color: '#0f1a33', stitch: { color: '#7fb3ff', pattern: 'single' } });
    setAll(doc, isSeatInsert, { material: 'leather_perforated', color: '#0f1a33', stitch: { color: '#7fb3ff', pattern: 'pleat' } });
    setAll(doc, isTrim, { material: 'anodized', color: '#1f3a7a' });
    allZones(doc, '#3d7bff', 0.7);
    doc.lighting.starlight = { ...doc.lighting.starlight, enabled: true, count: 500, colors: ['#cfe3ff', '#ffffff'], brightness: 0.8, twinkle: 0.6, twinkleSpeed: 0.8, pattern: 'random' };
  } },
  { id: 'racing', name: 'Racing Interior', description: 'Carbon racing shells, D-shape wheel, Alcantara, red accents', apply: (doc) => {
    doc.parts = factoryParts('jet_black');
    setAll(doc, isSoft, { material: 'alcantara', color: '#111113', stitch: { color: '#e03030', pattern: 'single' } });
    doc.parts['seats.driver.headrest'].variant = 'racing_shell';
    doc.parts['seats.passenger.headrest'].variant = 'racing_shell';
    doc.parts['steering.rim.upper'].variant = 'd_shape';
    setAll(doc, (id) => id.startsWith('steering.rim') || id.startsWith('steering.grip'), { material: 'alcantara', color: '#111113', stitch: { color: '#e03030', pattern: 'single' } });
    setAll(doc, (id) => id === 'steering.spokes' || id === 'steering.hub' || id.endsWith('.back.shell'), { material: 'carbon_twill', color: '#141416' });
    setAll(doc, (id) => id === 'pedals', { material: 'aluminum_brushed', color: '#a0a3a8' });
    setAll(doc, isTrim, { material: 'carbon_matte', color: '#141416' });
    setAll(doc, (id) => id.endsWith('.seatbelt'), { color: '#c8161d' });
  } },
  { id: 'rgb_night', name: 'RGB Night Show', description: 'Rainbow-cycling ambient zones and a dense starlight headliner', apply: (doc) => {
    doc.parts = factoryParts('jet_black');
    allZones(doc, '#ff00aa', 0.9);
    doc.lighting.master.mode = 'rainbow'; doc.lighting.master.speed = 1.2;
    doc.lighting.starlight = { ...doc.lighting.starlight, enabled: true, count: 900, colors: ['#ffffff', '#9fc9ff', '#ffd8a8', '#ff9fd6'], brightness: 1, twinkle: 0.8, twinkleSpeed: 1.4, shooting: true, pattern: 'milkyway' };
    doc.environment = 'night';
  } },
  { id: 'forged', name: 'Forged Carbon Edition', description: 'Forged carbon trim, two-tone black and gray leather', apply: (doc) => {
    doc.parts = factoryParts('jet_black');
    setAll(doc, isTrim, { material: 'carbon_forged', color: '#17181a' });
    setAll(doc, (id) => ['dash.glovebox', 'console.stack', 'console.trim', 'roof.panel', 'steering.hub', 'console.screen_bezel', 'cluster.bezel'].includes(id), { material: 'carbon_forged', color: '#17181a' });
    setAll(doc, isSeatInsert, { material: 'leather_perforated', color: '#5c5e61', stitch: { color: '#9a9a9e', pattern: 'pleat' } });
    setAll(doc, (id) => isSeat(id) && !isSeatInsert(id) && isSoft(id), { color: '#141416', stitch: { color: '#9a9a9e', pattern: 'single' } });
  } },
];

// ---------------------------------------------------------------------------
// Random generator with compatibility rules
// ---------------------------------------------------------------------------

export type RandomTheme = 'aggressive' | 'luxury' | 'futuristic' | 'factory_plus' | 'show_car' | 'racing';

interface ThemeSpec {
  soft: MaterialKind[]; trim: MaterialKind[]; palette: string[]; stitch: string[]; accentTrim: string[];
  wheels: string[]; seats: string[]; lighting: 'off' | 'solid' | 'animated'; starlight: number; patterns: PartConfig['stitch'] extends infer S ? (S extends { pattern: infer P } ? P[] : never) : never;
}

const THEMES: Record<RandomTheme, ThemeSpec> = {
  aggressive: { soft: ['alcantara', 'leather', 'suede'], trim: ['carbon_matte', 'carbon_gloss', 'anodized'], palette: ['#0f0f11', '#141416', '#1b1b1e'], stitch: ['#d2232a', '#ff5a1f', '#e8e8ec'], accentTrim: ['#b3161c', '#141416', '#2a2a2e'], wheels: ['flat_bottom', 'd_shape'], seats: ['competition', 'gt'], lighting: 'solid', starlight: 0.2, patterns: ['single', 'double'] },
  luxury: { soft: ['leather', 'leather_textured', 'leather_perforated'], trim: ['aluminum_polished', 'aluminum_brushed', 'chrome'], palette: ['#a98a62', '#4a3024', '#5c5e61', '#f0eadf', '#6a1116'], stitch: ['#5a4630', '#e6d9c3', '#9a9a9e'], accentTrim: ['#c9ccd2', '#8d9096'], wheels: ['factory'], seats: ['gt'], lighting: 'solid', starlight: 0.7, patterns: ['diamond', 'pleat', 'hex'] },
  futuristic: { soft: ['alcantara', 'woven', 'leather_gloss'], trim: ['anodized', 'titanium', 'carbon_colored', 'satin'], palette: ['#0b0f1a', '#0f1a33', '#1a1a1c', '#eef2ff'], stitch: ['#3d7bff', '#00e5ff', '#b26bff'], accentTrim: ['#1f3a7a', '#00a3b8', '#5a2d9c'], wheels: ['led_performance', 'd_shape'], seats: ['gt', 'competition'], lighting: 'animated', starlight: 0.9, patterns: ['hex', 'single'] },
  factory_plus: { soft: ['leather', 'leather_perforated'], trim: ['aluminum_brushed', 'carbon_twill'], palette: ['#141416', '#6a1116', '#a98a62', '#5c5e61'], stitch: ['#3a3a3e', '#8a2a2e', '#8c7250', '#e8e8ec'], accentTrim: ['#8d9096', '#141416'], wheels: ['factory'], seats: ['gt', 'competition'], lighting: 'off', starlight: 0, patterns: ['single', 'pleat'] },
  show_car: { soft: ['leather', 'leather_gloss', 'alcantara'], trim: ['chrome', 'carbon_colored', 'anodized', 'carbon_forged'], palette: ['#2b0a3d', '#0c3b2e', '#6a1116', '#0f1a33', '#f5f5f7'], stitch: ['#ffd166', '#ffffff', '#ff5aa5'], accentTrim: ['#d4af37', '#00c2a8', '#ff2d95'], wheels: ['led_performance', 'flat_bottom'], seats: ['gt', 'racing_shell'], lighting: 'animated', starlight: 1, patterns: ['diamond', 'hex'] },
  racing: { soft: ['alcantara', 'suede', 'fabric'], trim: ['carbon_twill', 'carbon_matte'], palette: ['#111113', '#1a1a1c'], stitch: ['#e03030', '#ffd400', '#ffffff'], accentTrim: ['#141416'], wheels: ['d_shape', 'flat_bottom'], seats: ['racing_shell', 'competition'], lighting: 'off', starlight: 0, patterns: ['single'] },
};

function rng(seed: number) {
  let s = seed >>> 0 || 1;
  return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return (s % 100000) / 100000; };
}
const pick = <T,>(r: () => number, arr: T[]): T => arr[Math.floor(r() * arr.length) % arr.length];

export function randomizeProject(doc: ProjectDoc, theme: RandomTheme, seed = Date.now()) {
  const t = THEMES[theme];
  const r = rng(seed);
  doc.parts = factoryParts('jet_black');
  const main = pick(r, t.palette);
  const secondary = pick(r, t.palette.filter((c) => c !== main).length ? t.palette.filter((c) => c !== main) : t.palette);
  const stitch = pick(r, t.stitch);
  const softMat = pick(r, t.soft);
  const trimMat = pick(r, t.trim);
  const accent = pick(r, t.accentTrim);
  const pattern = pick(r, t.patterns);
  const wheel = pick(r, t.wheels);
  const seatV = pick(r, t.seats);
  setAll(doc, isSoft, { material: softMat, color: main, stitch: { color: stitch, pattern: 'single' } });
  setAll(doc, isSeatInsert, { material: softMat === 'alcantara' ? 'alcantara' : 'leather_perforated', color: secondary, stitch: { color: stitch, pattern } });
  setAll(doc, isTrim, { material: trimMat, color: accent });
  setAll(doc, (id) => ['console.stack', 'console.trim', 'console.screen_bezel', 'cluster.bezel'].includes(id), { material: trimMat.startsWith('carbon') ? trimMat : 'plastic_gloss', color: trimMat.startsWith('carbon') ? '#141416' : '#0e0e10' });
  doc.parts['steering.rim.upper'].variant = wheel;
  // compatibility: LED and D-shape wheels use carbon spokes; racing shells have no headrest text
  if (wheel === 'led_performance' || wheel === 'd_shape') { doc.parts['steering.spokes'].material = 'carbon_twill'; doc.parts['steering.spokes'].color = '#141416'; }
  doc.parts['seats.driver.headrest'].variant = seatV;
  doc.parts['seats.passenger.headrest'].variant = seatV;
  if (seatV === 'racing_shell') {
    doc.parts['seats.driver.headrest'].text = '';
    doc.parts['seats.passenger.headrest'].text = '';
    setAll(doc, (id) => id.endsWith('.back.shell'), { material: 'carbon_twill', color: '#141416' });
  }
  if (t.lighting !== 'off') {
    const lc = pick(r, ['#ff1e1e', '#3d7bff', '#00e5ff', '#b26bff', '#ff2d95', '#ffffff', '#ffb300']);
    allZones(doc, lc, 0.6 + r() * 0.4);
    if (t.lighting === 'animated') doc.lighting.master.mode = pick(r, ['cycle', 'breathe', 'wave', 'rainbow']);
  } else {
    doc.lighting = defaultLighting();
  }
  if (r() < t.starlight) {
    doc.lighting.starlight = { ...doc.lighting.starlight, enabled: true, count: 300 + Math.floor(r() * 700), colors: [pick(r, ['#ffffff', '#cfe3ff', '#ffd8a8']), '#ffffff'], brightness: 0.6 + r() * 0.4, twinkle: r(), twinkleSpeed: 0.5 + r() * 1.5, shooting: r() < 0.5, pattern: pick(r, ['random', 'milkyway', 'constellation', 'spiral']) };
  }
  // keep variant lists valid
  for (const slot of ['steering', 'seats.driver', 'seats.passenger'] as const) {
    const ids = VARIANTS[slot].map((v) => v.id);
    const owner = slot === 'steering' ? 'steering.rim.upper' : `${slot}.headrest`;
    if (!ids.includes(doc.parts[owner].variant ?? '')) doc.parts[owner].variant = ids[0];
  }
}

export const RANDOM_THEMES: { id: RandomTheme; label: string }[] = [
  { id: 'aggressive', label: 'Aggressive' }, { id: 'luxury', label: 'Luxury' }, { id: 'futuristic', label: 'Futuristic' },
  { id: 'factory_plus', label: 'Factory Plus' }, { id: 'show_car', label: 'Show Car' }, { id: 'racing', label: 'Racing' },
];

export function summarizeProject(doc: ProjectDoc): string {
  const wheel = VARIANTS.steering.find((v) => v.id === doc.parts['steering.rim.upper']?.variant)?.label ?? 'Factory wheel';
  const seat = VARIANTS['seats.driver'].find((v) => v.id === doc.parts['seats.driver.headrest']?.variant)?.label ?? 'GT seat';
  const rim = doc.parts['steering.rim.upper']?.material ?? 'leather';
  const zones = Object.values(doc.lighting.zones).filter((z) => z.enabled).length;
  const bits = [wheel, seat, `${rim.replace('_', ' ')} rim`];
  if (zones) bits.push(`${zones} RGB zones`);
  if (doc.lighting.starlight.enabled) bits.push('starlight');
  return bits.join(' · ');
}
