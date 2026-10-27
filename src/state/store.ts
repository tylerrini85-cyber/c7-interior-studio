/** Single source of truth: current project document + UI state + undo/redo history. */
import { create } from 'zustand';
import { produce } from 'immer';
import type { ComponentId, EnvironmentId, PartConfig, ProjectDoc, ZoneId, LightingMaster, StarlightConfig, ElectronicsConfig, FactoryColorId } from '../project/schema';
import { SCHEMA_VERSION, defaultElectronics, defaultLighting, newId } from '../project/schema';
import { COMPONENT_MAP, factoryParts, VARIANT_SLOT_NODES, VARIANTS } from '../registry/components';
import { saveProject } from '../persistence/db';

export type Route = 'menu' | 'garage' | 'new' | 'studio' | 'settings' | 'help';
export type CameraMode = 'driver' | 'passenger' | 'free' | 'inspect';
export type SaveStatus = 'saved' | 'saving' | 'unsaved' | 'error' | 'idle';
export type Quality = 'ultra' | 'high' | 'balanced' | 'mobile';
export type Panel = 'parts' | 'inspector' | 'lighting' | 'none';

export interface Settings {
  quality: Quality;
  lookSensitivity: number;
  moveSpeed: number;
  invertY: boolean;
  arrowMode: 'look' | 'move';
  autosave: boolean;
  reduceMotion: boolean;
  showHints: boolean;
  defaultFov: number;
  cabinFill: number;   // 0..2, multiplier for the always-on interior fill lights
}

export interface AppState {
  route: Route;
  project: ProjectDoc | null;
  past: ProjectDoc[];
  future: ProjectDoc[];
  dirty: boolean;
  saveStatus: SaveStatus;
  lastProjectId: string | null;
  settings: Settings;
  // UI
  selected: ComponentId | null;
  hovered: ComponentId | null;
  focusTarget: { point: [number, number, number]; nonce: number } | null;
  cameraMode: CameraMode;
  cameraResetNonce: number;
  uiHidden: boolean;
  showroom: boolean;
  compareFactory: boolean;
  panel: Panel;
  mobileSheet: 'none' | 'parts' | 'inspector' | 'lighting' | 'camera';
  joystickVisible: boolean | null;   // null = automatic (shown on touch/mobile layouts)
  loading: { progress: number; label: string; error?: string } | null;
  toast: { id: number; text: string; kind: 'info' | 'error' | 'success' } | null;
  captureRequest: { nonce: number; mode: 'download' | 'thumbnail' | 'compare' } | null;
  compareImages: { before: string; after: string } | null;
  // actions
  setRoute: (r: Route) => void;
  loadProjectDoc: (doc: ProjectDoc) => void;
  createProject: (opts: { name: string; factoryColor: FactoryColorId; seat: 'driver' | 'passenger'; environment: EnvironmentId }) => ProjectDoc;
  updateProject: (fn: (draft: ProjectDoc) => void, opts?: { transient?: boolean; history?: boolean }) => void;
  setPart: (id: ComponentId, patch: Partial<PartConfig>, opts?: { transient?: boolean }) => void;
  setVariant: (slot: keyof typeof VARIANTS, variant: string) => void;
  setZone: (zone: ZoneId, patch: Partial<ProjectDoc['lighting']['zones'][ZoneId]>, opts?: { transient?: boolean }) => void;
  setMaster: (patch: Partial<LightingMaster>, opts?: { transient?: boolean }) => void;
  setStarlight: (patch: Partial<StarlightConfig>, opts?: { transient?: boolean }) => void;
  setMatSparkle: (patch: Partial<StarlightConfig>, opts?: { transient?: boolean }) => void;
  setElectronics: (patch: Partial<ElectronicsConfig>) => void;
  setEnvironment: (env: EnvironmentId) => void;
  resetPartToFactory: (id: ComponentId) => void;
  resetToFactory: () => void;
  renameProject: (name: string) => void;
  undo: () => void;
  redo: () => void;
  commitTransient: () => void;
  select: (id: ComponentId | null) => void;
  hover: (id: ComponentId | null) => void;
  focusOn: (id: ComponentId) => void;
  setCameraMode: (m: CameraMode) => void;
  resetCamera: () => void;
  toggleUi: (v?: boolean) => void;
  setShowroom: (v: boolean) => void;
  setCompareFactory: (v: boolean) => void;
  setPanel: (p: Panel) => void;
  setMobileSheet: (s: AppState['mobileSheet']) => void;
  setJoystickVisible: (v: boolean | null) => void;
  setLoading: (l: AppState['loading']) => void;
  notify: (text: string, kind?: 'info' | 'error' | 'success') => void;
  requestCapture: (mode: 'download' | 'thumbnail' | 'compare') => void;
  setCompareImages: (imgs: AppState['compareImages']) => void;
  setSettings: (patch: Partial<Settings>) => void;
  saveNow: () => Promise<void>;
  setThumbnail: (dataUrl: string) => void;
}

const HISTORY_LIMIT = 150;

const isMobile = typeof navigator !== 'undefined' && /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);

export const DEFAULT_SETTINGS: Settings = {
  quality: isMobile ? 'mobile' : 'high', lookSensitivity: 1, moveSpeed: 1, invertY: false, arrowMode: 'look', autosave: true,
  reduceMotion: false, showHints: true, defaultFov: 75, cabinFill: 1,
};

let saveTimer: ReturnType<typeof setTimeout> | null = null;
let transientBase: ProjectDoc | null = null;

export const useStore = create<AppState>((set, get) => {
  const scheduleSave = () => {
    const s = get();
    if (!s.settings.autosave || !s.project) return;
    if (saveTimer) clearTimeout(saveTimer);
    set({ saveStatus: 'unsaved' });
    saveTimer = setTimeout(() => { void get().saveNow(); }, 1200);
  };

  const applyDoc = (next: ProjectDoc, opts?: { transient?: boolean; history?: boolean }) => {
    const s = get();
    const prev = s.project;
    if (!prev) return;
    const transient = !!opts?.transient;
    const history = opts?.history !== false;
    const stamped = { ...next, updatedAt: new Date().toISOString() };
    if (transient) {
      if (!transientBase) transientBase = prev;
      set({ project: stamped, dirty: true });
      return;
    }
    const base = transientBase ?? prev;
    transientBase = null;
    const past = history ? [...s.past.slice(-HISTORY_LIMIT + 1), base] : s.past;
    set({ project: stamped, past, future: history ? [] : s.future, dirty: true });
    scheduleSave();
  };

  return {
    route: 'menu',
    project: null,
    past: [],
    future: [],
    dirty: false,
    saveStatus: 'idle',
    lastProjectId: null,
    settings: DEFAULT_SETTINGS,
    selected: null,
    hovered: null,
    focusTarget: null,
    cameraMode: 'driver',
    cameraResetNonce: 0,
    uiHidden: false,
    showroom: false,
    compareFactory: false,
    panel: 'parts',
    mobileSheet: 'none',
    joystickVisible: null,
    loading: null,
    toast: null,
    captureRequest: null,
    compareImages: null,

    setRoute: (route) => set({ route }),

    loadProjectDoc: (doc) => {
      transientBase = null;
      set({ project: doc, past: [], future: [], dirty: false, saveStatus: 'saved', selected: null, hovered: null, lastProjectId: doc.id, cameraMode: doc.camera.seat, compareFactory: false, route: 'studio', panel: 'parts', mobileSheet: 'none' });
    },

    createProject: ({ name, factoryColor, seat, environment }) => {
      const now = new Date().toISOString();
      const doc: ProjectDoc = {
        schemaVersion: SCHEMA_VERSION, id: newId(), name: name.trim() || 'Untitled project', createdAt: now, updatedAt: now,
        base: { year: 2019, trim: '3LT', seats: 'GT', transmission: 'A8', body: 'coupe', factoryColor },
        parts: factoryParts(factoryColor), lighting: defaultLighting(), electronics: defaultElectronics(), environment,
        camera: { seat, eyeHeight: 0, fov: get().settings.defaultFov }, linkSeats: true, linkDoors: true,
      };
      get().loadProjectDoc(doc);
      set({ dirty: true, saveStatus: 'unsaved' });
      void get().saveNow();
      return doc;
    },

    updateProject: (fn, opts) => {
      const prev = get().project;
      if (!prev) return;
      applyDoc(produce(prev, fn), opts);
    },

    setPart: (id, patch, opts) => {
      const prev = get().project;
      if (!prev) return;
      const next = produce(prev, (d) => {
        const apply = (cid: ComponentId) => {
          const cur = d.parts[cid];
          if (!cur) return;
          d.parts[cid] = { ...cur, ...patch };
        };
        apply(id);
        // linked seats / doors mirror the change to the counterpart component
        if (d.linkSeats && id.startsWith('seats.')) apply(id.startsWith('seats.driver') ? id.replace('seats.driver', 'seats.passenger') : id.replace('seats.passenger', 'seats.driver'));
        if (d.linkDoors && id.startsWith('doors.')) apply(id.startsWith('doors.driver') ? id.replace('doors.driver', 'doors.passenger') : id.replace('doors.passenger', 'doors.driver'));
      });
      applyDoc(next, opts);
    },

    setVariant: (slot, variant) => {
      const owner = slot === 'steering' ? 'steering.rim.upper' : slot === 'shifter' ? 'console.shifter' : `${slot}.headrest`;
      get().setPart(owner, { variant });
    },

    setZone: (zone, patch, opts) => get().updateProject((d) => { d.lighting.zones[zone] = { ...d.lighting.zones[zone], ...patch }; }, opts),
    setMaster: (patch, opts) => get().updateProject((d) => {
      d.lighting.master = { ...d.lighting.master, ...patch };
      if (d.lighting.master.sync && patch.color) for (const z of Object.keys(d.lighting.zones) as ZoneId[]) d.lighting.zones[z].color = patch.color;
    }, opts),
    setStarlight: (patch, opts) => get().updateProject((d) => { d.lighting.starlight = { ...d.lighting.starlight, ...patch }; }, opts),
    setMatSparkle: (patch, opts) => get().updateProject((d) => { d.lighting.matSparkle = { ...d.lighting.matSparkle, ...patch }; }, opts),
    setElectronics: (patch) => get().updateProject((d) => { d.electronics = { ...d.electronics, ...patch }; }),
    setEnvironment: (env) => get().updateProject((d) => { d.environment = env; }, { history: false }),

    resetPartToFactory: (id) => {
      const def = COMPONENT_MAP.get(id);
      const prev = get().project;
      if (!def || !prev) return;
      const fp = factoryParts(prev.base.factoryColor)[id];
      get().setPart(id, fp);
    },
    resetToFactory: () => get().updateProject((d) => { d.parts = factoryParts(d.base.factoryColor); d.lighting = defaultLighting(); d.electronics = defaultElectronics(); }),
    renameProject: (name) => get().updateProject((d) => { d.name = name.trim() || d.name; }, { history: false }),

    undo: () => {
      const s = get();
      if (!s.project || !s.past.length) return;
      const prev = s.past[s.past.length - 1];
      set({ project: prev, past: s.past.slice(0, -1), future: [s.project, ...s.future].slice(0, HISTORY_LIMIT), dirty: true });
      scheduleSave();
    },
    redo: () => {
      const s = get();
      if (!s.project || !s.future.length) return;
      const next = s.future[0];
      set({ project: next, past: [...s.past, s.project].slice(-HISTORY_LIMIT), future: s.future.slice(1), dirty: true });
      scheduleSave();
    },
    commitTransient: () => {
      const s = get();
      if (!transientBase || !s.project) return;
      const base = transientBase;
      transientBase = null;
      set({ past: [...s.past.slice(-HISTORY_LIMIT + 1), base], future: [] });
      scheduleSave();
    },

    select: (id) => set({ selected: id, panel: id ? 'inspector' : get().panel }),
    hover: (id) => set({ hovered: id }),
    focusOn: (id) => {
      const def = COMPONENT_MAP.get(id);
      set({ selected: id, panel: 'inspector' });
      if (def?.focus) set({ focusTarget: { point: def.focus, nonce: Date.now() } });
    },
    setCameraMode: (m) => set({ cameraMode: m }),
    resetCamera: () => set((s) => ({ cameraResetNonce: s.cameraResetNonce + 1, cameraMode: s.project?.camera.seat ?? 'driver' })),
    toggleUi: (v) => set((s) => ({ uiHidden: v ?? !s.uiHidden })),
    setShowroom: (v) => set({ showroom: v, uiHidden: v }),
    setCompareFactory: (v) => set({ compareFactory: v }),
    setPanel: (p) => set({ panel: p }),
    setMobileSheet: (sheet) => set({ mobileSheet: sheet }),
    setJoystickVisible: (v) => set({ joystickVisible: v }),
    setLoading: (loading) => set({ loading }),
    notify: (text, kind = 'info') => set({ toast: { id: Date.now(), text, kind } }),
    requestCapture: (mode) => set({ captureRequest: { nonce: Date.now(), mode } }),
    setCompareImages: (compareImages) => set({ compareImages }),
    setSettings: (patch) => set((s) => ({ settings: { ...s.settings, ...patch } })),

    saveNow: async () => {
      const s = get();
      if (!s.project) return;
      set({ saveStatus: 'saving' });
      try {
        await saveProject(s.project);
        set({ saveStatus: 'saved', dirty: false, lastProjectId: s.project.id });
      } catch (e) {
        console.error(e);
        set({ saveStatus: 'error' });
        get().notify('Could not save project (storage error)', 'error');
      }
    },
    setThumbnail: (dataUrl) => {
      const prev = get().project;
      if (!prev) return;
      set({ project: { ...prev, thumbnail: dataUrl } });
      scheduleSave();
    },
  };
});

/** Project document to render: the factory document when "compare" is active. */
let compareCache: { source: ProjectDoc; doc: ProjectDoc } | null = null;
export function selectRenderDoc(s: AppState): ProjectDoc | null {
  if (!s.project) return null;
  if (!s.compareFactory) return s.project;
  // memoized: selectors must return a stable reference for the same inputs
  if (!compareCache || compareCache.source !== s.project) {
    compareCache = { source: s.project, doc: { ...s.project, parts: factoryParts(s.project.base.factoryColor), lighting: defaultLighting() } };
  }
  return compareCache.doc;
}

export function variantForSlot(doc: ProjectDoc, slot: keyof typeof VARIANTS): string {
  const owner = slot === 'steering' ? 'steering.rim.upper' : slot === 'shifter' ? 'console.shifter' : `${slot}.headrest`;
  return doc.parts[owner]?.variant ?? VARIANTS[slot][0].id;
}

export { VARIANT_SLOT_NODES };
