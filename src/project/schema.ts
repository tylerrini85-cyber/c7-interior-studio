/** Project document schema (v1). The single source of truth for a customized interior. */

export const SCHEMA_VERSION = 1 as const;

export type ComponentId = string;
export type ZoneId =
  | 'dash' | 'console' | 'footwell.driver' | 'footwell.passenger' | 'door.driver' | 'door.passenger'
  | 'handles' | 'cupholders' | 'seats' | 'storage';

export type MaterialKind =
  | 'leather' | 'leather_perforated' | 'leather_textured' | 'leather_gloss' | 'alcantara' | 'suede' | 'fabric' | 'woven'
  | 'carbon_twill' | 'carbon_forged' | 'carbon_matte' | 'carbon_gloss' | 'carbon_colored'
  | 'aluminum_brushed' | 'aluminum_polished' | 'chrome' | 'titanium' | 'steel_brushed' | 'anodized'
  | 'plastic_gloss' | 'plastic_matte' | 'plastic_soft' | 'paint' | 'satin' | 'polymer_textured' | 'carpet'
  | 'glass' | 'screen' | 'rubber' | 'emissive';

export type Finish = 'matte' | 'satin' | 'gloss';
export type StitchPattern = 'none' | 'single' | 'double' | 'diamond' | 'pleat' | 'hex';

export interface StitchConfig {
  color: string;
  pattern: StitchPattern;
}

export interface PartConfig {
  material: MaterialKind;
  color: string;
  color2?: string;
  accent?: string;
  finish?: Finish;
  stitch?: StitchConfig;
  variant?: string;
  text?: string;
  textColor?: string;
  hidden?: boolean;
}

export type LightMode = 'solid' | 'cycle' | 'rainbow' | 'breathe' | 'pulse' | 'wave' | 'alternate' | 'glow';

export interface ZoneConfig {
  enabled: boolean;
  color: string;
  brightness: number; // 0..1
}

export interface LightingMaster {
  enabled: boolean;
  brightness: number;   // 0..1
  saturation: number;   // 0..1
  mode: LightMode;
  speed: number;        // 0.1..3
  sync: boolean;        // all zones follow master color
  color: string;
}

export type StarPattern = 'random' | 'constellation' | 'grid' | 'spiral' | 'milkyway';

export interface StarlightConfig {
  enabled: boolean;
  count: number;          // 50..1500
  colors: string[];       // 1..4 colors
  brightness: number;     // 0..1
  twinkle: number;        // 0..1 intensity
  twinkleSpeed: number;   // 0.1..3
  shooting: boolean;
  pattern: StarPattern;
  seed: number;
  size: number;           // 0.5..2
}

export type EnvironmentId = 'day' | 'sunset' | 'night' | 'showroom';
export type FactoryColorId = 'jet_black' | 'adrenaline_red' | 'kalahari' | 'gray' | 'brownstone';
export type GaugeTheme = 'tour' | 'sport' | 'track' | 'concept_neon' | 'concept_minimal';

export interface ElectronicsConfig {
  gaugeTheme: GaugeTheme;
  gaugeColor: string;
  infotainmentTheme: 'factory' | 'concept_dark' | 'concept_red' | 'concept_blue';
  brightness: number;
  startupLogo: 'factory_placeholder' | 'custom_text';
  startupText?: string;
}

export interface CameraPrefs {
  seat: 'driver' | 'passenger';
  eyeHeight: number; // -0.08..0.08 m offset
  fov: number;
}

export interface ProjectBase {
  year: 2019;
  trim: '3LT';
  seats: 'GT';
  transmission: 'A8';
  body: 'coupe';
  factoryColor: FactoryColorId;
}

export interface ProjectDoc {
  schemaVersion: typeof SCHEMA_VERSION;
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
  base: ProjectBase;
  parts: Record<ComponentId, PartConfig>;
  lighting: { master: LightingMaster; zones: Record<ZoneId, ZoneConfig>; starlight: StarlightConfig };
  electronics: ElectronicsConfig;
  environment: EnvironmentId;
  camera: CameraPrefs;
  thumbnail?: string;
  linkSeats: boolean;
  linkDoors: boolean;
}

export const ZONE_IDS: ZoneId[] = ['dash', 'console', 'footwell.driver', 'footwell.passenger', 'door.driver', 'door.passenger', 'handles', 'cupholders', 'seats', 'storage'];

export const ZONE_LABELS: Record<ZoneId, string> = {
  dash: 'Dashboard edge', console: 'Center console', 'footwell.driver': 'Driver footwell', 'footwell.passenger': 'Passenger footwell',
  'door.driver': 'Driver door trim', 'door.passenger': 'Passenger door trim', handles: 'Door handles', cupholders: 'Cupholders',
  seats: 'Seat bases', storage: 'Storage areas',
};

export function defaultLighting(): ProjectDoc['lighting'] {
  const zones = {} as Record<ZoneId, ZoneConfig>;
  for (const z of ZONE_IDS) zones[z] = { enabled: false, color: '#ff2a2a', brightness: 0.7 };
  return {
    master: { enabled: false, brightness: 0.7, saturation: 1, mode: 'solid', speed: 1, sync: true, color: '#ff2a2a' },
    zones,
    starlight: { enabled: false, count: 400, colors: ['#ffffff'], brightness: 0.8, twinkle: 0.5, twinkleSpeed: 1, shooting: false, pattern: 'random', seed: 7, size: 1 },
  };
}

export function defaultElectronics(): ElectronicsConfig {
  return { gaugeTheme: 'tour', gaugeColor: '#ff3b30', infotainmentTheme: 'factory', brightness: 0.8, startupLogo: 'factory_placeholder' };
}

export function newId(): string {
  const c = (globalThis.crypto as Crypto | undefined);
  if (c && 'randomUUID' in c) return c.randomUUID();
  return 'p_' + Math.random().toString(36).slice(2) + Date.now().toString(36);
}

/** Migrate any older document shape to the current schema. */
export function migrate(doc: unknown): ProjectDoc {
  const d = doc as Partial<ProjectDoc> & Record<string, unknown>;
  if (!d || typeof d !== 'object') throw new Error('Invalid project document');
  // v0 (pre-release) had no schemaVersion; fill in defaults for anything missing.
  const lighting = defaultLighting();
  const out: ProjectDoc = {
    schemaVersion: SCHEMA_VERSION,
    id: typeof d.id === 'string' ? d.id : newId(),
    name: typeof d.name === 'string' ? d.name : 'Untitled project',
    createdAt: typeof d.createdAt === 'string' ? d.createdAt : new Date().toISOString(),
    updatedAt: typeof d.updatedAt === 'string' ? d.updatedAt : new Date().toISOString(),
    base: { year: 2019, trim: '3LT', seats: 'GT', transmission: 'A8', body: 'coupe', factoryColor: (d.base?.factoryColor as FactoryColorId) ?? 'jet_black' },
    parts: (d.parts as Record<ComponentId, PartConfig>) ?? {},
    lighting: {
      master: { ...lighting.master, ...(d.lighting?.master ?? {}) },
      zones: { ...lighting.zones, ...(d.lighting?.zones ?? {}) },
      starlight: { ...lighting.starlight, ...(d.lighting?.starlight ?? {}) },
    },
    electronics: { ...defaultElectronics(), ...(d.electronics ?? {}) },
    environment: (d.environment as EnvironmentId) ?? 'showroom',
    camera: { seat: 'driver', eyeHeight: 0, fov: 75, ...(d.camera ?? {}) },
    thumbnail: typeof d.thumbnail === 'string' ? d.thumbnail : undefined,
    linkSeats: typeof d.linkSeats === 'boolean' ? d.linkSeats : true,
    linkDoors: typeof d.linkDoors === 'boolean' ? d.linkDoors : true,
  };
  return out;
}
