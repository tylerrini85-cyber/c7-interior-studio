import { describe, it, expect, beforeEach } from 'vitest';
import { useStore } from './store';
import { factoryParts, COMPONENTS, COMPONENT_MAP } from '../registry/components';
import { migrate, defaultLighting } from '../project/schema';
import { PRESETS, randomizeProject, summarizeProject } from '../project/presets';
import { parseImportedProject, exportProjectJson } from '../persistence/db';

// idb is not available in jsdom: stub saveProject by disabling autosave
beforeEach(() => { useStore.setState({ project: null, past: [], future: [], settings: { ...useStore.getState().settings, autosave: false } }); });

const create = () => useStore.getState().createProject({ name: 'T', factoryColor: 'jet_black', seat: 'driver', environment: 'showroom' });

describe('registry', () => {
  it('has a factory config for every component and valid materials', () => {
    const parts = factoryParts('jet_black');
    for (const c of COMPONENTS) {
      expect(parts[c.id]).toBeTruthy();
      expect(c.caps.materials).toContain(parts[c.id].material);
    }
    expect(new Set(COMPONENTS.map((c) => c.id)).size).toBe(COMPONENTS.length);
  });
  it('applies factory interior colors to soft trim', () => {
    expect(factoryParts('adrenaline_red')['dash.upper'].color).toBe('#6a1116');
    expect(factoryParts('kalahari')['seats.driver.base.center'].color).toBe('#a98a62');
  });
});

describe('store', () => {
  it('creates independent projects', () => {
    const a = create();
    const b = create();
    expect(a.id).not.toBe(b.id);
  });
  it('setPart records history and supports undo/redo', () => {
    create();
    const s = useStore.getState();
    s.setPart('steering.rim.upper', { material: 'alcantara' });
    expect(useStore.getState().project!.parts['steering.rim.upper'].material).toBe('alcantara');
    expect(useStore.getState().past.length).toBe(1);
    useStore.getState().undo();
    expect(useStore.getState().project!.parts['steering.rim.upper'].material).toBe('leather');
    useStore.getState().redo();
    expect(useStore.getState().project!.parts['steering.rim.upper'].material).toBe('alcantara');
  });
  it('transient edits collapse into one history step', () => {
    create();
    const s = useStore.getState();
    s.setPart('dash.upper', { color: '#111111' }, { transient: true });
    s.setPart('dash.upper', { color: '#222222' }, { transient: true });
    s.setPart('dash.upper', { color: '#333333' }, { transient: true });
    useStore.getState().commitTransient();
    expect(useStore.getState().past.length).toBe(1);
    useStore.getState().undo();
    expect(useStore.getState().project!.parts['dash.upper'].color).toBe('#141416');
  });
  it('linked seats mirror changes; unlinked do not', () => {
    create();
    useStore.getState().setPart('seats.driver.headrest', { material: 'suede' });
    expect(useStore.getState().project!.parts['seats.passenger.headrest'].material).toBe('suede');
    useStore.getState().updateProject((d) => { d.linkSeats = false; });
    useStore.getState().setPart('seats.driver.headrest', { material: 'fabric' });
    expect(useStore.getState().project!.parts['seats.passenger.headrest'].material).toBe('suede');
  });
  it('part changes never leak to unrelated parts', () => {
    create();
    const before = JSON.stringify(useStore.getState().project!.parts['console.main']);
    useStore.getState().setPart('steering.hub', { material: 'carbon_twill', color: '#ff0000' });
    expect(JSON.stringify(useStore.getState().project!.parts['console.main'])).toBe(before);
  });
  it('factory reset restores every part', () => {
    create();
    useStore.getState().setPart('doors.driver.upper', { material: 'alcantara', color: '#00ff00' });
    useStore.getState().resetToFactory();
    expect(useStore.getState().project!.parts).toEqual(factoryParts('jet_black'));
  });
  it('variants are set on the slot owner', () => {
    create();
    useStore.getState().setVariant('steering', 'd_shape');
    expect(useStore.getState().project!.parts['steering.rim.upper'].variant).toBe('d_shape');
    useStore.getState().setVariant('seats.driver', 'competition');
    expect(useStore.getState().project!.parts['seats.driver.headrest'].variant).toBe('competition');
  });
});

describe('presets and randomizer', () => {
  it('every preset keeps materials within component capabilities', () => {
    for (const p of PRESETS) {
      const doc = create();
      useStore.getState().updateProject((d) => p.apply(d));
      const parts = useStore.getState().project!.parts;
      for (const c of COMPONENTS) expect(c.caps.materials, `${p.id}:${c.id}`).toContain(parts[c.id].material);
      void doc;
    }
  });
  it('randomizer produces compatible designs for every theme', () => {
    for (const t of ['aggressive', 'luxury', 'futuristic', 'factory_plus', 'show_car', 'racing'] as const) {
      for (let seed = 1; seed < 6; seed++) {
        create();
        useStore.getState().updateProject((d) => randomizeProject(d, t, seed));
        const d = useStore.getState().project!;
        for (const c of COMPONENTS) expect(c.caps.materials, `${t}/${seed}/${c.id}`).toContain(d.parts[c.id].material);
        if (d.parts['seats.driver.headrest'].variant === 'racing_shell') expect(d.parts['seats.driver.headrest'].text ?? '').toBe('');
      }
    }
  });
  it('summarizes a project', () => { create(); expect(summarizeProject(useStore.getState().project!)).toContain('GT seat'); });
});

describe('schema migration and import/export', () => {
  it('migrates a minimal legacy document', () => {
    const doc = migrate({ id: 'x', name: 'Old', parts: {} });
    expect(doc.schemaVersion).toBe(1);
    expect(doc.lighting).toEqual(defaultLighting());
    expect(doc.camera.seat).toBe('driver');
  });
  it('round-trips through export/import', () => {
    const doc = create();
    const text = exportProjectJson(useStore.getState().project!);
    const back = parseImportedProject(text);
    expect(back.id).toBe(doc.id);
    expect(back.parts).toEqual(useStore.getState().project!.parts);
  });
  it('rejects garbage', () => { expect(() => parseImportedProject('null')).toThrow(); });
  it('component map resolves ids', () => { expect(COMPONENT_MAP.get('steering.hub')?.label).toBe('Center hub'); });
});
