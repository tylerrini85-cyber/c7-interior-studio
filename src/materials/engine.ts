/** Material engine: converts a PartConfig into a MeshPhysicalMaterial with physically meaningful parameters
 *  and consistent texture scale (UVs are in meters, so repeat = tiles per meter). */
import * as THREE from 'three';
import type { MaterialKind, PartConfig, Finish } from '../project/schema';
import { alcantaraMaps, brushedMetalMaps, carbonTwillMaps, carpetMaps, fabricMaps, forgedCarbonMaps, leatherNormal, leatherRoughness, perforationMaps, stitchMap } from './textures';

export interface MaterialPreset {
  label: string;
  group: 'Leather' | 'Fabric & suede' | 'Carbon fiber' | 'Metal' | 'Plastic & paint' | 'Other';
  roughness: number; metalness: number; clearcoat?: number; clearcoatRoughness?: number; sheen?: number; sheenRoughness?: number;
  normalScale?: number; repeat: number; maps?: () => { normal?: THREE.Texture; roughness?: THREE.Texture; color?: THREE.Texture };
  colorMultiply?: number; anisotropy?: number; tintColorMap?: boolean; envMapIntensity?: number;
}

export const MATERIAL_PRESETS: Record<MaterialKind, MaterialPreset> = {
  leather: { label: 'Smooth Napa leather', group: 'Leather', roughness: 0.58, metalness: 0, normalScale: 0.55, repeat: 2.5, maps: () => ({ normal: leatherNormal('fine'), roughness: leatherRoughness() }) },
  leather_textured: { label: 'Textured leather', group: 'Leather', roughness: 0.7, metalness: 0, normalScale: 1.0, repeat: 2.0, maps: () => ({ normal: leatherNormal('coarse'), roughness: leatherRoughness() }) },
  leather_perforated: { label: 'Perforated leather', group: 'Leather', roughness: 0.62, metalness: 0, normalScale: 0.9, repeat: 3.5, maps: () => ({ normal: perforationMaps().normal, roughness: perforationMaps().roughness }) },
  leather_gloss: { label: 'Gloss-treated leather', group: 'Leather', roughness: 0.35, metalness: 0, clearcoat: 0.5, clearcoatRoughness: 0.25, normalScale: 0.5, repeat: 2.5, maps: () => ({ normal: leatherNormal('fine') }) },
  alcantara: { label: 'Alcantara-style microfiber', group: 'Fabric & suede', roughness: 0.95, metalness: 0, sheen: 0.9, sheenRoughness: 0.8, normalScale: 0.6, repeat: 4, maps: () => ({ normal: alcantaraMaps().normal, roughness: alcantaraMaps().roughness }) },
  suede: { label: 'Suede', group: 'Fabric & suede', roughness: 0.98, metalness: 0, sheen: 0.7, sheenRoughness: 0.9, normalScale: 0.5, repeat: 4, maps: () => ({ normal: alcantaraMaps().normal }) },
  fabric: { label: 'Performance fabric', group: 'Fabric & suede', roughness: 0.9, metalness: 0, sheen: 0.4, normalScale: 0.8, repeat: 6, maps: () => ({ normal: fabricMaps().normal, roughness: fabricMaps().roughness }) },
  woven: { label: 'Custom woven upholstery', group: 'Fabric & suede', roughness: 0.85, metalness: 0, sheen: 0.5, normalScale: 1.2, repeat: 8, maps: () => ({ normal: fabricMaps().normal }) },
  carbon_twill: { label: 'Twill carbon fiber', group: 'Carbon fiber', roughness: 0.3, metalness: 0.1, clearcoat: 0.8, clearcoatRoughness: 0.12, normalScale: 0.7, repeat: 6, maps: () => carbonTwillMaps(), tintColorMap: true },
  carbon_gloss: { label: 'Gloss carbon fiber', group: 'Carbon fiber', roughness: 0.2, metalness: 0.1, clearcoat: 1.0, clearcoatRoughness: 0.05, normalScale: 0.6, repeat: 6, maps: () => carbonTwillMaps(), tintColorMap: true },
  carbon_matte: { label: 'Matte carbon fiber', group: 'Carbon fiber', roughness: 0.6, metalness: 0.05, clearcoat: 0.1, clearcoatRoughness: 0.6, normalScale: 0.8, repeat: 6, maps: () => carbonTwillMaps(), tintColorMap: true },
  carbon_colored: { label: 'Colored carbon weave', group: 'Carbon fiber', roughness: 0.25, metalness: 0.1, clearcoat: 0.9, clearcoatRoughness: 0.08, normalScale: 0.7, repeat: 6, maps: () => carbonTwillMaps(), tintColorMap: true, colorMultiply: 2.2 },
  carbon_forged: { label: 'Forged carbon', group: 'Carbon fiber', roughness: 0.28, metalness: 0.05, clearcoat: 0.9, clearcoatRoughness: 0.1, normalScale: 0.5, repeat: 3, maps: () => forgedCarbonMaps(), tintColorMap: true },
  aluminum_brushed: { label: 'Brushed aluminum', group: 'Metal', roughness: 0.42, metalness: 1, normalScale: 0.35, repeat: 2, maps: () => brushedMetalMaps(), anisotropy: 0.6 },
  aluminum_polished: { label: 'Polished aluminum', group: 'Metal', roughness: 0.12, metalness: 1, repeat: 1 },
  chrome: { label: 'Chrome', group: 'Metal', roughness: 0.04, metalness: 1, repeat: 1 },
  titanium: { label: 'Titanium finish', group: 'Metal', roughness: 0.38, metalness: 1, normalScale: 0.25, repeat: 2, maps: () => brushedMetalMaps(), anisotropy: 0.4 },
  steel_brushed: { label: 'Brushed steel', group: 'Metal', roughness: 0.48, metalness: 1, normalScale: 0.4, repeat: 2, maps: () => brushedMetalMaps(), anisotropy: 0.7 },
  anodized: { label: 'Anodized metal', group: 'Metal', roughness: 0.3, metalness: 0.9, repeat: 1, normalScale: 0.15, maps: () => brushedMetalMaps() },
  plastic_gloss: { label: 'Gloss black plastic', group: 'Plastic & paint', roughness: 0.08, metalness: 0, clearcoat: 0.6, clearcoatRoughness: 0.05, repeat: 1 },
  plastic_matte: { label: 'Matte plastic', group: 'Plastic & paint', roughness: 0.75, metalness: 0, repeat: 1 },
  plastic_soft: { label: 'Soft-touch plastic', group: 'Plastic & paint', roughness: 0.68, metalness: 0, normalScale: 0.3, repeat: 3, maps: () => ({ normal: alcantaraMaps().normal }) },
  paint: { label: 'Automotive paint', group: 'Plastic & paint', roughness: 0.25, metalness: 0.2, clearcoat: 1, clearcoatRoughness: 0.04, repeat: 1 },
  satin: { label: 'Satin finish', group: 'Plastic & paint', roughness: 0.45, metalness: 0.3, clearcoat: 0.3, clearcoatRoughness: 0.4, repeat: 1 },
  polymer_textured: { label: 'Textured polymer', group: 'Plastic & paint', roughness: 0.85, metalness: 0, normalScale: 1.4, repeat: 5, maps: () => ({ normal: leatherNormal('coarse') }) },
  carpet: { label: 'Carpet', group: 'Other', roughness: 1, metalness: 0, sheen: 0.3, normalScale: 1.2, repeat: 6, maps: () => carpetMaps() },
  rubber: { label: 'Rubber', group: 'Other', roughness: 0.85, metalness: 0, repeat: 1 },
  glass: { label: 'Glass', group: 'Other', roughness: 0, metalness: 0, repeat: 1 },
  screen: { label: 'Screen', group: 'Other', roughness: 0.1, metalness: 0, repeat: 1 },
  emissive: { label: 'Emissive', group: 'Other', roughness: 0.5, metalness: 0, repeat: 1 },
};

export const MATERIAL_GROUPS = ['Leather', 'Fabric & suede', 'Carbon fiber', 'Metal', 'Plastic & paint', 'Other'] as const;

const finishAdjust: Record<Finish, { r: number; cc: number }> = { matte: { r: 0.25, cc: -0.4 }, satin: { r: 0, cc: 0 }, gloss: { r: -0.2, cc: 0.4 } };

export function configKey(cfg: PartConfig): string {
  return [cfg.material, cfg.color, cfg.color2 ?? '', cfg.accent ?? '', cfg.finish ?? '', cfg.stitch?.pattern ?? '', cfg.stitch?.color ?? ''].join('|');
}

/** Build a material for a configuration. UV repeat is scaled by the preset repeat (tiles per meter). */
export function buildMaterial(cfg: PartConfig, opts: { uvScale?: number; stitchAllowed?: boolean; quality?: 'low' | 'high' } = {}): THREE.MeshPhysicalMaterial {
  const p = MATERIAL_PRESETS[cfg.material] ?? MATERIAL_PRESETS.plastic_matte;
  const mat = new THREE.MeshPhysicalMaterial();
  mat.name = configKey(cfg);
  const col = new THREE.Color(cfg.color);
  if (p.colorMultiply) col.multiplyScalar(p.colorMultiply);
  mat.color.copy(col);
  mat.roughness = p.roughness; mat.metalness = p.metalness;
  mat.clearcoat = p.clearcoat ?? 0; mat.clearcoatRoughness = p.clearcoatRoughness ?? 0.2;
  mat.sheen = p.sheen ?? 0; mat.sheenRoughness = p.sheenRoughness ?? 0.8; mat.sheenColor.copy(col).lerp(new THREE.Color('#ffffff'), 0.5);
  mat.envMapIntensity = p.envMapIntensity ?? 1;
  if (cfg.finish) { const f = finishAdjust[cfg.finish]; mat.roughness = THREE.MathUtils.clamp(mat.roughness + f.r, 0.02, 1); mat.clearcoat = THREE.MathUtils.clamp(mat.clearcoat + f.cc, 0, 1); }
  const repeat = p.repeat * (opts.uvScale ?? 1);
  const maps = opts.quality === 'low' && p.group !== 'Carbon fiber' ? undefined : p.maps?.();
  if (maps?.normal) { mat.normalMap = maps.normal.clone(); mat.normalMap.repeat.set(repeat, repeat); mat.normalMap.needsUpdate = true; mat.normalScale.set(p.normalScale ?? 1, p.normalScale ?? 1); }
  if (maps?.roughness) { mat.roughnessMap = maps.roughness.clone(); mat.roughnessMap.repeat.set(repeat, repeat); mat.roughnessMap.needsUpdate = true; }
  if (maps?.color && p.tintColorMap) { mat.map = maps.color.clone(); mat.map.repeat.set(repeat, repeat); mat.map.needsUpdate = true; mat.color.copy(col).multiplyScalar(p.colorMultiply ? 1 : 3.2); }
  if (p.anisotropy && 'anisotropy' in mat) { mat.anisotropy = p.anisotropy; }
  if (cfg.material === 'glass') { mat.transparent = true; mat.opacity = 0.18; mat.roughness = 0.05; mat.color.set('#9fb3c8'); mat.depthWrite = false; mat.side = THREE.DoubleSide; }
  if (cfg.material === 'emissive') { mat.emissive.copy(col); mat.emissiveIntensity = 2; }
  // stitching: drawn as an alpha overlay via the emissive map trick is unreliable; use a second material layer (decal) instead -> see StitchOverlay in Cockpit.
  return mat;
}

export function stitchOverlayMaterial(cfg: PartConfig, uvScale = 1): THREE.MeshStandardMaterial | null {
  if (!cfg.stitch || cfg.stitch.pattern === 'none') return null;
  const tex = stitchMap(cfg.stitch.pattern, cfg.stitch.color).clone();
  const rep = (cfg.stitch.pattern === 'pleat' ? 1 : cfg.stitch.pattern === 'diamond' || cfg.stitch.pattern === 'hex' ? 2.5 : 1) * uvScale;
  tex.repeat.set(rep, rep); tex.needsUpdate = true;
  const m = new THREE.MeshStandardMaterial({ map: tex, transparent: true, roughness: 0.8, metalness: 0, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, alphaTest: 0.05 });
  m.color.set('#ffffff');
  return m;
}

/** Fixed materials for non-customizable GLB nodes, keyed by the GLB material name. */
export function fixedMaterialFor(glbMaterialName: string): PartConfig {
  const n = glbMaterialName.replace(/\.\d+$/, '');
  switch (n) {
    case 'plastic_black_gloss': return { material: 'plastic_gloss', color: '#0e0e10' };
    case 'plastic_black': return { material: 'plastic_matte', color: '#121214' };
    case 'plastic_soft': return { material: 'plastic_soft', color: '#121214' };
    case 'metal_brushed': return { material: 'aluminum_brushed', color: '#8d9096' };
    case 'metal_satin_dark': return { material: 'anodized', color: '#3a3c40' };
    case 'chrome': return { material: 'chrome', color: '#d8d8dc' };
    case 'carbon': return { material: 'carbon_twill', color: '#141416' };
    case 'rubber': return { material: 'rubber', color: '#141416' };
    case 'carpet_black': return { material: 'carpet', color: '#111113' };
    case 'leather_black': return { material: 'leather', color: '#141416' };
    case 'leather_black_perf': return { material: 'leather_perforated', color: '#141416' };
    case 'suede_black': case 'headliner_suede': return { material: 'suede', color: '#1a1a1c' };
    case 'glass': return { material: 'glass', color: '#dfe6ee' };
    case 'screen_off': return { material: 'screen', color: '#05060a' };
    case 'mirror': return { material: 'chrome', color: '#f0f0f4' };
    case 'emblem': return { material: 'paint', color: '#b3161c' };
    case 'emissive_white': return { material: 'emissive', color: '#fff6e0' };
    case 'stitch_grey': return { material: 'fabric', color: '#9a9a9e' };
    case 'seatbelt': return { material: 'woven', color: '#161618' };
    default: return { material: 'plastic_matte', color: '#1a1a1c' };
  }
}
