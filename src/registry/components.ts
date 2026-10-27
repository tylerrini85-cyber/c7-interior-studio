/** Component registry: stable ids for every customizable interior part, their capabilities, groups and factory config. */
import type { ComponentId, MaterialKind, PartConfig, FactoryColorId } from '../project/schema';

export type Category =
  | 'steering' | 'dashboard' | 'console' | 'seats' | 'doors' | 'roof' | 'lighting' | 'floor' | 'trim' | 'electronics' | 'accessories' | 'pillars';

export const CATEGORY_LABELS: Record<Category, string> = {
  steering: 'Steering Wheel', dashboard: 'Dashboard', console: 'Center Console', seats: 'Seats', doors: 'Door Panels',
  roof: 'Headliner & Roof', lighting: 'Lighting', floor: 'Floor & Carpets', trim: 'Trim', electronics: 'Electronics',
  accessories: 'Accessories', pillars: 'Pillars',
};

export const CATEGORY_ORDER: Category[] = ['steering', 'dashboard', 'console', 'seats', 'doors', 'roof', 'lighting', 'floor', 'trim', 'electronics', 'accessories', 'pillars'];

export type VariantSlot = 'steering' | 'seats.driver' | 'seats.passenger' | 'shifter';

export interface Capabilities {
  materials: MaterialKind[];
  color2?: boolean;
  accent?: boolean;
  stitch?: boolean;
  text?: boolean;
  variantSlot?: VariantSlot;
  finish?: boolean;
}

export interface ComponentDef {
  id: ComponentId;
  label: string;
  category: Category;
  group: string;          // UI grouping, e.g. 'Driver seat'
  nodes: string[];        // GLB node name prefixes mapped to this component
  caps: Capabilities;
  factory: PartConfig;
  /** camera focus point in three.js coords (x, y, z) for "focus" from the parts menu */
  focus?: [number, number, number];
}

const CARBON: MaterialKind[] = ['carbon_twill', 'carbon_gloss', 'carbon_matte', 'carbon_forged', 'carbon_colored'];
// Carbon fiber is offered on every part (soft trims included) so any surface can be wrapped.
const SOFT: MaterialKind[] = ['leather', 'leather_perforated', 'leather_textured', 'leather_gloss', 'alcantara', 'suede', 'fabric', 'woven', ...CARBON];
const HARD: MaterialKind[] = ['carbon_twill', 'carbon_forged', 'carbon_matte', 'carbon_gloss', 'carbon_colored', 'aluminum_brushed', 'aluminum_polished', 'chrome', 'titanium', 'steel_brushed', 'anodized', 'plastic_gloss', 'plastic_matte', 'plastic_soft', 'paint', 'satin', 'polymer_textured'];
const ALL: MaterialKind[] = [...SOFT, ...HARD];
const CARPETS: MaterialKind[] = ['carpet', 'fabric', 'rubber', 'leather', ...CARBON];

export const FACTORY_COLORS: Record<FactoryColorId, { label: string; main: string; accent: string; stitch: string; carpet: string }> = {
  jet_black: { label: 'Jet Black', main: '#141416', accent: '#1b1b1e', stitch: '#3a3a3e', carpet: '#111113' },
  adrenaline_red: { label: 'Adrenaline Red', main: '#6a1116', accent: '#141416', stitch: '#8a2a2e', carpet: '#111113' },
  kalahari: { label: 'Kalahari', main: '#a98a62', accent: '#141416', stitch: '#8c7250', carpet: '#2a241c' },
  gray: { label: 'Gray', main: '#5c5e61', accent: '#141416', stitch: '#7a7c80', carpet: '#1a1a1c' },
  brownstone: { label: 'Brownstone', main: '#4a3024', accent: '#141416', stitch: '#6a4a3a', carpet: '#1a1512' },
};

const F = (material: MaterialKind, color: string, extra: Partial<PartConfig> = {}): PartConfig => ({ material, color, ...extra });

function seat(prefix: 'seats.driver' | 'seats.passenger', label: string, group: string): ComponentDef[] {
  const fx = prefix === 'seats.driver' ? -0.37 : 0.37;
  const focus: [number, number, number] = [fx, 0.6, 0.05];
  return [
    { id: `${prefix}.base.center`, label: `${label} cushion insert`, category: 'seats', group, nodes: [`${prefix}.base.center`], caps: { materials: SOFT, stitch: true, color2: true }, factory: F('leather_perforated', '#141416', { stitch: { color: '#3a3a3e', pattern: 'pleat' } }), focus },
    { id: `${prefix}.base.bolsters`, label: `${label} cushion bolsters`, category: 'seats', group, nodes: [`${prefix}.base.bolsters`], caps: { materials: SOFT, stitch: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'single' } }), focus },
    { id: `${prefix}.back.center`, label: `${label} backrest insert`, category: 'seats', group, nodes: [`${prefix}.back.center`], caps: { materials: SOFT, stitch: true, color2: true }, factory: F('leather_perforated', '#141416', { stitch: { color: '#3a3a3e', pattern: 'pleat' } }), focus },
    { id: `${prefix}.back.bolsters`, label: `${label} backrest bolsters`, category: 'seats', group, nodes: [`${prefix}.back.bolsters`], caps: { materials: SOFT, stitch: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'single' } }), focus },
    { id: `${prefix}.headrest`, label: `${label} headrest`, category: 'seats', group, nodes: [`${prefix}.headrest`, `${prefix}.headrest.neck`], caps: { materials: SOFT, stitch: true, text: true, variantSlot: prefix }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'single' }, variant: 'gt', text: '', textColor: '#9a9a9e' }), focus },
    { id: `${prefix}.back.shell`, label: `${label} back shell`, category: 'seats', group, nodes: [`${prefix}.back.shell`], caps: { materials: HARD }, factory: F('plastic_matte', '#121214'), focus },
    { id: `${prefix}.seatbelt`, label: `${label} seatbelt`, category: 'seats', group, nodes: [`${prefix}.seatbelt`], caps: { materials: ['fabric', 'woven', 'carbon_twill'] }, factory: F('woven', '#161618'), focus },
  ];
}

function door(prefix: 'doors.driver' | 'doors.passenger', label: string): ComponentDef[] {
  const fx = prefix === 'doors.driver' ? -0.65 : 0.65;
  const focus: [number, number, number] = [fx, 0.6, -0.05];
  const group = `${label} door`;
  return [
    { id: `${prefix}.upper`, label: `${label} door upper trim`, category: 'doors', group, nodes: [`${prefix}.upper`], caps: { materials: SOFT, stitch: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'none' } }), focus },
    { id: `${prefix}.panel`, label: `${label} door panel`, category: 'doors', group, nodes: [`${prefix}.panel`], caps: { materials: SOFT, stitch: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'none' } }), focus },
    { id: `${prefix}.lower`, label: `${label} door lower trim`, category: 'doors', group, nodes: [`${prefix}.lower`, `${prefix}.pocket`], caps: { materials: [...HARD, 'carpet'] }, factory: F('plastic_soft', '#121214'), focus },
    { id: `${prefix}.armrest`, label: `${label} door armrest`, category: 'doors', group, nodes: [`${prefix}.armrest`, `${prefix}.pull`], caps: { materials: SOFT, stitch: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'none' } }), focus },
    { id: `${prefix}.handle`, label: `${label} door handle`, category: 'doors', group, nodes: [`${prefix}.handle`], caps: { materials: HARD }, factory: F('aluminum_brushed', '#8d9096'), focus },
    { id: `${prefix}.speaker`, label: `${label} door speaker surround`, category: 'doors', group, nodes: [`${prefix}.speaker_ring`], caps: { materials: HARD }, factory: F('plastic_soft', '#121214'), focus },
    { id: `${prefix}.trim`, label: `${label} door accent insert`, category: 'doors', group, nodes: [`${prefix}.trim`], caps: { materials: HARD, accent: true }, factory: F('aluminum_brushed', '#8d9096'), focus },
  ];
}

export const COMPONENTS: ComponentDef[] = [
  // steering
  { id: 'steering.rim.upper', label: 'Upper rim', category: 'steering', group: 'Steering wheel', nodes: ['steering.rim.upper'], caps: { materials: SOFT, stitch: true, variantSlot: 'steering' }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'single' }, variant: 'factory' }), focus: [-0.37, 0.66, -0.46] },
  { id: 'steering.rim.lower', label: 'Lower rim', category: 'steering', group: 'Steering wheel', nodes: ['steering.rim.lower'], caps: { materials: SOFT, stitch: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'single' } }), focus: [-0.37, 0.66, -0.46] },
  { id: 'steering.grip.left', label: 'Left grip', category: 'steering', group: 'Steering wheel', nodes: ['steering.grip.left'], caps: { materials: SOFT, stitch: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'single' } }), focus: [-0.37, 0.66, -0.46] },
  { id: 'steering.grip.right', label: 'Right grip', category: 'steering', group: 'Steering wheel', nodes: ['steering.grip.right'], caps: { materials: SOFT, stitch: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'single' } }), focus: [-0.37, 0.66, -0.46] },
  { id: 'steering.spokes', label: 'Spokes', category: 'steering', group: 'Steering wheel', nodes: ['steering.spoke.left', 'steering.spoke.right', 'steering.spoke.lower'], caps: { materials: HARD }, factory: F('aluminum_brushed', '#3a3c40'), focus: [-0.37, 0.66, -0.46] },
  { id: 'steering.spokes.insert', label: 'Accent insert', category: 'steering', group: 'Steering wheel', nodes: ['steering.spoke.lower.insert'], caps: { materials: HARD, accent: true }, factory: F('aluminum_brushed', '#8d9096'), focus: [-0.37, 0.66, -0.46] },
  { id: 'steering.hub', label: 'Center hub', category: 'steering', group: 'Steering wheel', nodes: ['steering.hub'], caps: { materials: [...SOFT, ...HARD] }, factory: F('plastic_soft', '#141416'), focus: [-0.37, 0.66, -0.46] },
  { id: 'steering.paddles', label: 'Paddle shifters', category: 'steering', group: 'Steering wheel', nodes: ['steering.paddle.left', 'steering.paddle.right'], caps: { materials: HARD }, factory: F('aluminum_brushed', '#3a3c40'), focus: [-0.37, 0.66, -0.46] },
  { id: 'column.shroud', label: 'Column shroud', category: 'steering', group: 'Steering wheel', nodes: ['column.shroud', 'column.stalk.left', 'column.stalk.right'], caps: { materials: HARD }, factory: F('plastic_soft', '#121214'), focus: [-0.37, 0.66, -0.56] },
  // dashboard
  { id: 'dash.upper', label: 'Upper dash pad', category: 'dashboard', group: 'Dashboard', nodes: ['dash.upper', 'dash.end.driver', 'dash.end.passenger'], caps: { materials: SOFT, stitch: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'none' } }), focus: [0, 0.85, -0.75] },
  { id: 'dash.trim.driver', label: 'Driver dash trim', category: 'dashboard', group: 'Dashboard', nodes: ['dash.trim.driver'], caps: { materials: ALL, accent: true }, factory: F('leather', '#141416'), focus: [-0.6, 0.72, -0.62] },
  { id: 'dash.trim.passenger', label: 'Passenger dash trim', category: 'dashboard', group: 'Dashboard', nodes: ['dash.trim.passenger'], caps: { materials: ALL, accent: true }, factory: F('leather', '#141416'), focus: [0.45, 0.72, -0.62] },
  { id: 'dash.grab', label: 'Cockpit wrap & grab handle', category: 'dashboard', group: 'Dashboard', nodes: ['dash.grab', 'dash.welt', 'console.bolster.driver'], caps: { materials: SOFT, stitch: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'none' } }), focus: [0.22, 0.7, -0.52] },
  { id: 'dash.grab_trim', label: 'Grab handle trim', category: 'dashboard', group: 'Dashboard', nodes: ['dash.grab_trim'], caps: { materials: HARD, accent: true }, factory: F('aluminum_brushed', '#8d9096'), focus: [0.22, 0.7, -0.5] },
  { id: 'dash.vents', label: 'Air vents', category: 'dashboard', group: 'Dashboard', nodes: ['dash.vents.driver.ring', 'dash.vents.passenger.ring', 'dash.vents.passenger_inner.ring', 'dash.vents.center.left', 'dash.vents.center.right', 'dash.passenger_switches.ring', 'console.badge_strip', 'console.hvac_knob.left', 'console.hvac_knob.right'], caps: { materials: HARD }, factory: F('aluminum_brushed', '#3a3c40'), focus: [-0.6, 0.75, -0.66] },
  { id: 'dash.lower', label: 'Under-dash panels', category: 'dashboard', group: 'Dashboard', nodes: ['dash.under', 'dash.switch_panel', 'dash.defroster', 'dash.center_speaker'], caps: { materials: HARD }, factory: F('plastic_soft', '#121214'), focus: [-0.4, 0.45, -0.72] },
  { id: 'cluster.bezel', label: 'Instrument cluster bezel', category: 'dashboard', group: 'Dashboard', nodes: ['cluster.bezel'], caps: { materials: HARD }, factory: F('plastic_soft', '#121214'), focus: [-0.37, 0.78, -0.74] },
  // center stack / console
  { id: 'console.stack', label: 'Center stack body', category: 'console', group: 'Center console', nodes: ['console.stack'], caps: { materials: ALL, stitch: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'single' } }), focus: [0.02, 0.7, -0.55] },
  { id: 'console.hvac', label: 'Climate control panel', category: 'console', group: 'Center console', nodes: ['console.hvac'], caps: { materials: HARD }, factory: F('plastic_soft', '#121214'), focus: [0.02, 0.62, -0.5] },
  { id: 'console.main', label: 'Console body', category: 'console', group: 'Center console', nodes: ['console.main'], caps: { materials: ALL, stitch: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'single' } }), focus: [0, 0.56, -0.1] },
  { id: 'console.lid', label: 'Console storage lid', category: 'console', group: 'Center console', nodes: ['console.cupholder_plate', 'console.small_switches'], caps: { materials: HARD }, factory: F('plastic_gloss', '#0e0e10'), focus: [0.06, 0.56, -0.2] },
  { id: 'console.trim', label: 'Console trim plate', category: 'console', group: 'Center console', nodes: ['console.trim'], caps: { materials: HARD, accent: true }, factory: F('aluminum_brushed', '#8d9096'), focus: [0, 0.56, -0.26] },
  { id: 'console.shifter', label: 'Shifter', category: 'console', group: 'Center console', nodes: ['console.shifter.knob', 'console.shifter.lever'], caps: { materials: [...SOFT, ...HARD], variantSlot: 'shifter' }, factory: F('leather', '#141416', { variant: 'automatic' }), focus: [0, 0.65, -0.26] },
  { id: 'console.shifter.boot', label: 'Shifter boot', category: 'console', group: 'Center console', nodes: ['console.shifter.boot'], caps: { materials: SOFT, stitch: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'single' } }), focus: [0, 0.6, -0.26] },
  { id: 'console.shifter.ring', label: 'Shifter ring', category: 'console', group: 'Center console', nodes: ['console.shifter.ring'], caps: { materials: ['chrome', 'aluminum_polished', 'aluminum_brushed', 'anodized', 'titanium', ...CARBON] }, factory: F('chrome', '#d8d8dc'), focus: [0, 0.65, -0.26] },
  { id: 'console.dial', label: 'Drive mode dial', category: 'console', group: 'Center console', nodes: ['console.drive_mode_dial'], caps: { materials: HARD }, factory: F('aluminum_brushed', '#3a3c40'), focus: [-0.08, 0.58, -0.14] },
  { id: 'console.armrest', label: 'Armrest lid', category: 'console', group: 'Center console', nodes: ['console.armrest'], caps: { materials: SOFT, stitch: true, text: true }, factory: F('leather', '#141416', { stitch: { color: '#3a3a3e', pattern: 'single' }, text: '' }), focus: [0, 0.62, 0.27] },
  { id: 'console.screen_bezel', label: 'Infotainment bezel', category: 'console', group: 'Center console', nodes: ['console.screen_bezel'], caps: { materials: HARD }, factory: F('plastic_gloss', '#0e0e10'), focus: [0.02, 0.74, -0.55] },
  // seats
  ...seat('seats.driver', 'Driver', 'Driver seat'),
  ...seat('seats.passenger', 'Passenger', 'Passenger seat'),
  // doors
  ...door('doors.driver', 'Driver'),
  ...door('doors.passenger', 'Passenger'),
  // roof
  { id: 'roof.headliner', label: 'Headliner', category: 'roof', group: 'Headliner & roof', nodes: ['roof.header', 'roof.rear_strip', 'roof.rail.driver', 'roof.rail.passenger'], caps: { materials: SOFT, stitch: true }, factory: F('suede', '#1a1a1c', { stitch: { color: '#2a2a2e', pattern: 'none' } }), focus: [0, 1.05, 0.05] },
  { id: 'roof.panel', label: 'Removable roof panel', category: 'roof', group: 'Headliner & roof', nodes: ['roof.panel'], caps: { materials: SOFT, stitch: true }, factory: F('suede', '#1a1a1c', { stitch: { color: '#2a2a2e', pattern: 'none' } }), focus: [0, 1.05, 0.1] },
  { id: 'roof.visors', label: 'Sun visors', category: 'roof', group: 'Headliner & roof', nodes: ['roof.visor.driver', 'roof.visor.passenger'], caps: { materials: SOFT }, factory: F('suede', '#1a1a1c'), focus: [-0.36, 1.02, -0.45] },
  { id: 'pillars', label: 'A-pillars & header', category: 'pillars', group: 'Headliner & roof', nodes: ['pillar.a.driver', 'pillar.a.passenger', 'pillar.header', 'pillar.halo'], caps: { materials: SOFT }, factory: F('suede', '#1a1a1c'), focus: [-0.6, 0.95, -0.7] },
  { id: 'pillars.b', label: 'B-pillar trim', category: 'pillars', group: 'Headliner & roof', nodes: ['pillar.b.driver', 'pillar.b.passenger'], caps: { materials: [...SOFT, ...HARD] }, factory: F('plastic_soft', '#121214'), focus: [-0.65, 0.6, 0.55] },
  { id: 'mirror.body', label: 'Rear-view mirror', category: 'accessories', group: 'Accessories', nodes: ['mirror.body', 'mirror.stalk'], caps: { materials: HARD }, factory: F('plastic_matte', '#121214'), focus: [0, 0.93, -0.52] },
  { id: 'roof.overhead_console', label: 'Overhead console', category: 'roof', group: 'Headliner & roof', nodes: ['roof.overhead_console'], caps: { materials: HARD }, factory: F('plastic_soft', '#121214'), focus: [0, 1.05, -0.36] },
  // floor
  { id: 'floor.carpet', label: 'Carpet', category: 'floor', group: 'Floor', nodes: ['floor.carpet', 'trim.kick.driver', 'trim.kick.passenger', 'rear.bulkhead', 'rear.cargo_floor', 'rear.quarter.driver', 'rear.quarter.passenger'], caps: { materials: CARPETS }, factory: F('carpet', '#111113'), focus: [-0.3, 0.1, -0.4] },
  { id: 'floor.mats.driver', label: 'Driver floor mat', category: 'floor', group: 'Floor', nodes: ['floor.mats.driver'], caps: { materials: CARPETS, stitch: true, text: true }, factory: F('carpet', '#111113', { stitch: { color: '#3a3a3e', pattern: 'single' }, text: 'CORVETTE', textColor: '#c8c8cc' }), focus: [-0.39, 0.1, -0.42] },
  { id: 'floor.mats.passenger', label: 'Passenger floor mat', category: 'floor', group: 'Floor', nodes: ['floor.mats.passenger'], caps: { materials: CARPETS, stitch: true, text: true }, factory: F('carpet', '#111113', { stitch: { color: '#3a3a3e', pattern: 'single' }, text: 'CORVETTE', textColor: '#c8c8cc' }), focus: [0.39, 0.1, -0.42] },
  { id: 'pedals', label: 'Pedal covers', category: 'floor', group: 'Floor', nodes: ['pedals.brake', 'pedals.accelerator', 'pedals.dead_pedal'], caps: { materials: ['rubber', 'aluminum_brushed', 'aluminum_polished', 'steel_brushed', 'anodized', ...CARBON] }, factory: F('rubber', '#141416'), focus: [-0.35, 0.2, -0.86] },
  { id: 'sills', label: 'Sill plates', category: 'trim', group: 'Trim', nodes: ['doors.driver.sill_plate', 'doors.passenger.sill_plate'], caps: { materials: HARD, text: true }, factory: F('aluminum_brushed', '#8d9096', { text: 'C7 STINGRAY' }), focus: [-0.64, 0.2, -0.05] },
];

export const COMPONENT_MAP: Map<ComponentId, ComponentDef> = new Map(COMPONENTS.map((c) => [c.id, c]));

/** Nodes that are not customizable keep a fixed material derived from their GLB material name. */
export function componentForNode(nodeName: string): ComponentDef | undefined {
  // exact match first, then longest prefix match (node names are dotted paths)
  const exact = NODE_INDEX.get(nodeName);
  if (exact) return exact;
  let best: ComponentDef | undefined;
  let bestLen = 0;
  for (const [prefix, def] of NODE_INDEX) {
    if (nodeName.startsWith(prefix + '.') && prefix.length > bestLen) { best = def; bestLen = prefix.length; }
  }
  return best;
}

const NODE_INDEX = new Map<string, ComponentDef>();
for (const c of COMPONENTS) for (const n of c.nodes) NODE_INDEX.set(n, c);

export function factoryParts(color: FactoryColorId = 'jet_black'): Record<ComponentId, PartConfig> {
  const fc = FACTORY_COLORS[color];
  const parts: Record<ComponentId, PartConfig> = {};
  for (const c of COMPONENTS) {
    const p: PartConfig = JSON.parse(JSON.stringify(c.factory));
    if (c.factory.color === '#141416' && p.material !== 'carpet') {
      // main upholstery color follows the factory interior color on soft-trim parts
      if (SOFT.includes(p.material) || p.material === 'plastic_soft' && c.category === 'steering') p.color = fc.main;
      if (p.stitch) p.stitch = { ...p.stitch, color: fc.stitch };
    }
    if (p.material === 'carpet') p.color = fc.carpet;
    parts[c.id] = p;
  }
  return parts;
}

export const VARIANTS: Record<VariantSlot, { id: string; label: string; file?: string; description: string }[]> = {
  steering: [
    { id: 'factory', label: 'Factory Stingray wheel', description: '14.1 in round three-spoke wheel' },
    { id: 'flat_bottom', label: 'Flat-bottom (Z06 / ZR1 style)', file: 'variants/steering_flat_bottom.glb', description: 'Thicker rim with a flat bottom and trim insert' },
    { id: 'd_shape', label: 'Custom performance D-shape', file: 'variants/steering_d_shape.glb', description: 'Flat top and bottom, center marker' },
    { id: 'led_performance', label: 'LED performance wheel', file: 'variants/steering_led_performance.glb', description: 'D-shape with shift-light LED strip' },
  ],
  'seats.driver': [
    { id: 'gt', label: 'GT seat (factory)', description: 'Standard GT seat with integrated headrest' },
    { id: 'competition', label: 'Competition Sport', file: 'variants/seats_competition.glb', description: 'Deeper bolsters, harness pass-throughs' },
    { id: 'racing_shell', label: 'Carbon racing shell', file: 'variants/seats_racing_shell.glb', description: 'Fixed-back bucket with head surround' },
  ],
  'seats.passenger': [
    { id: 'gt', label: 'GT seat (factory)', description: 'Standard GT seat with integrated headrest' },
    { id: 'competition', label: 'Competition Sport', file: 'variants/seats_competition.glb', description: 'Deeper bolsters, harness pass-throughs' },
    { id: 'racing_shell', label: 'Carbon racing shell', file: 'variants/seats_racing_shell.glb', description: 'Fixed-back bucket with head surround' },
  ],
  shifter: [
    { id: 'automatic', label: '8-speed automatic (factory)', description: 'Leather boot, leather knob with chrome ring' },
    { id: 'manual', label: '7-speed manual (concept)', file: 'variants/shifter_manual.glb', description: 'Taller lever, round knob' },
    { id: 'short_throw', label: 'Short-throw manual (concept)', file: 'variants/shifter_short_throw.glb', description: 'Short lever, round knob' },
  ],
};

/** Node prefixes replaced by each variant slot */
export const VARIANT_SLOT_NODES: Record<VariantSlot, string[]> = {
  steering: ['steering.'],
  'seats.driver': ['seats.driver.'],
  'seats.passenger': ['seats.passenger.'],
  shifter: ['console.shifter.'],
};
