/** RGB lighting zones, master controls, dynamic modes, starlight headliner, electronics themes, environment. */
import { useState } from 'react';
import { useStore } from '../state/store';
import { ZONE_IDS, ZONE_LABELS, type LightMode, type StarPattern, type EnvironmentId, type GaugeTheme } from '../project/schema';
import { getSetting, setSetting } from '../persistence/db';
import { Button, ColorPicker, Section, Segmented, Select, Slider, Toggle } from './common';

const LIGHT_PRESETS = [
  { name: 'Corvette Red', color: '#ff1e1e' }, { name: 'Ice Blue', color: '#3d7bff' }, { name: 'Cyan', color: '#00e5ff' }, { name: 'Violet', color: '#b26bff' },
  { name: 'Magenta', color: '#ff2d95' }, { name: 'Amber', color: '#ffb300' }, { name: 'Warm White', color: '#fff1d6' }, { name: 'Emerald', color: '#1fd27a' },
];

interface SavedLighting { name: string; lighting: ReturnType<typeof useStore.getState>['project'] extends infer P ? P extends { lighting: infer L } ? L : never : never }

const STAR_PALETTES: { name: string; colors: string[] }[] = [
  { name: 'Warm white', colors: ['#fff1d6'] }, { name: 'Cool white', colors: ['#ffffff'] }, { name: 'Ice blue', colors: ['#cfe3ff', '#ffffff'] },
  { name: 'Purple', colors: ['#b26bff', '#e0c8ff'] }, { name: 'Red', colors: ['#ff3b30', '#ff9a8a'] }, { name: 'Amber', colors: ['#ffb300', '#fff1d6'] },
  { name: 'Teal', colors: ['#00e5ff', '#9ffcff'] }, { name: 'Multicolor', colors: ['#ffffff', '#9fc9ff', '#ffd8a8', '#ff9fd6'] },
];

/** Starlight headliner controls (shared by the Lighting tab and the headliner inspector). */
export function StarlightControls({ open = true }: { open?: boolean }) {
  const project = useStore((s) => s.project);
  const setStarlight = useStore((s) => s.setStarlight);
  const commit = useStore((s) => s.commitTransient);
  if (!project) return null;
  const { starlight } = project.lighting;
  return (
    <Section title="Starlight headliner" defaultOpen={open} right={<Toggle label="" value={starlight.enabled} onChange={(v) => setStarlight({ enabled: v })} />}>
      {!starlight.enabled && <p className="muted small">Switch on to embed fiber-optic style stars in the headliner and roof panel.</p>}
      <div className="field"><span className="field-label">Star color presets</span>
        <div className="material-chips">{STAR_PALETTES.map((p) => <button type="button" key={p.name} className={`chip-btn ${JSON.stringify(starlight.colors) === JSON.stringify(p.colors) ? 'sel' : ''}`} onClick={() => setStarlight({ enabled: true, colors: p.colors })}><span className="mini-swatch" style={{ display: 'inline-block', width: 12, height: 12, marginRight: 6, verticalAlign: -1, background: p.colors[0] }} />{p.name}</button>)}</div>
      </div>
      <div className="field"><span className="field-label">Custom star colors</span>
        <div className="star-colors">
          {starlight.colors.map((c, i) => <ColorPicker key={i} value={c} onChange={(nc) => setStarlight({ colors: starlight.colors.map((x, j) => (j === i ? nc : x)) }, { transient: true })} onCommit={commit} compact />)}
          <div className="row-actions">
            {starlight.colors.length < 4 && <Button size="sm" icon="plus" onClick={() => setStarlight({ colors: [...starlight.colors, '#9fc9ff'] })}>Add color</Button>}
            {starlight.colors.length > 1 && <Button size="sm" icon="close" onClick={() => setStarlight({ colors: starlight.colors.slice(0, -1) })}>Remove</Button>}
          </div>
        </div>
      </div>
      <Slider label="Number of stars" value={starlight.count} min={50} max={1500} step={10} onChange={(v) => setStarlight({ count: v }, { transient: true })} onCommit={commit} format={(v) => `${v}`} />
      <Select<StarPattern> label="Pattern" value={starlight.pattern} onChange={(p) => setStarlight({ pattern: p })} options={[{ value: 'random', label: 'Randomized' }, { value: 'milkyway', label: 'Milky Way band' }, { value: 'constellation', label: 'Constellation clusters' }, { value: 'grid', label: 'Even grid' }, { value: 'spiral', label: 'Spiral' }]} />
      <Slider label="Brightness" value={starlight.brightness} min={0} max={1} onChange={(v) => setStarlight({ brightness: v }, { transient: true })} onCommit={commit} />
      <Slider label="Star size" value={starlight.size} min={0.5} max={2} onChange={(v) => setStarlight({ size: v }, { transient: true })} onCommit={commit} />
      <Slider label="Twinkle intensity" value={starlight.twinkle} min={0} max={1} onChange={(v) => setStarlight({ twinkle: v }, { transient: true })} onCommit={commit} />
      <Slider label="Twinkle speed" value={starlight.twinkleSpeed} min={0.1} max={3} onChange={(v) => setStarlight({ twinkleSpeed: v }, { transient: true })} onCommit={commit} />
      <Toggle label="Shooting stars" value={starlight.shooting} onChange={(v) => setStarlight({ shooting: v })} />
      <Button size="sm" icon="dice" onClick={() => setStarlight({ seed: Math.floor(Math.random() * 1e6) })}>Re-roll pattern</Button>
    </Section>
  );
}

export function LightingPanel() {
  const project = useStore((s) => s.project);
  const setZone = useStore((s) => s.setZone);
  const setMaster = useStore((s) => s.setMaster);
  const setElectronics = useStore((s) => s.setElectronics);
  const setEnvironment = useStore((s) => s.setEnvironment);
  const updateProject = useStore((s) => s.updateProject);
  const commit = useStore((s) => s.commitTransient);
  const notify = useStore((s) => s.notify);
  const [saved, setSaved] = useState<SavedLighting[] | null>(null);
  if (!project) return null;
  const { master, zones } = project.lighting;
  const loadSaved = async () => { const list = await getSetting<SavedLighting[]>('lightingPresets', []); setSaved(list); return list; };
  if (saved === null) void loadSaved();

  return (
    <div className="lighting-panel">
      <Section title="Environment">
        <Segmented<EnvironmentId> ariaLabel="Lighting condition" value={project.environment} onChange={setEnvironment} options={[{ value: 'day', label: 'Day', icon: 'sun' }, { value: 'sunset', label: 'Sunset', icon: 'sunset' }, { value: 'night', label: 'Night', icon: 'moon' }, { value: 'showroom', label: 'Showroom', icon: 'showroom' }]} />
      </Section>
      <Section title="Ambient RGB lighting" right={<Toggle label="" value={master.enabled} onChange={(v) => setMaster({ enabled: v })} />}>
        <ColorPicker label="Master color" value={master.color} onChange={(c) => setMaster({ color: c }, { transient: true })} onCommit={commit} compact />
        <div className="light-presets">{LIGHT_PRESETS.map((p) => <button type="button" key={p.name} className="mini-swatch" style={{ background: p.color }} title={p.name} onClick={() => setMaster({ color: p.color, enabled: true })} />)}</div>
        <Slider label="Master brightness" value={master.brightness} min={0} max={1} onChange={(v) => setMaster({ brightness: v }, { transient: true })} onCommit={commit} />
        <Slider label="Saturation" value={master.saturation} min={0} max={1} onChange={(v) => setMaster({ saturation: v }, { transient: true })} onCommit={commit} />
        <Select<LightMode> label="Mode" value={master.mode} onChange={(m) => setMaster({ mode: m })} options={[{ value: 'solid', label: 'Solid color' }, { value: 'glow', label: 'Soft ambient glow' }, { value: 'cycle', label: 'Slow color cycle' }, { value: 'rainbow', label: 'Rainbow transition' }, { value: 'breathe', label: 'Breathing' }, { value: 'pulse', label: 'Pulsing' }, { value: 'wave', label: 'Wave' }, { value: 'alternate', label: 'Alternating zones' }]} />
        {master.mode !== 'solid' && <Slider label="Speed" value={master.speed} min={0.1} max={3} step={0.05} onChange={(v) => setMaster({ speed: v }, { transient: true })} onCommit={commit} />}
        <Toggle label="Sync all zones to master color" value={master.sync} onChange={(v) => setMaster({ sync: v, color: master.color })} />
        <div className="row-actions">
          <Button size="sm" onClick={() => updateProject((d) => { for (const z of ZONE_IDS) d.lighting.zones[z].enabled = true; d.lighting.master.enabled = true; })}>All zones on</Button>
          <Button size="sm" onClick={() => updateProject((d) => { for (const z of ZONE_IDS) d.lighting.zones[z].enabled = false; })}>All zones off</Button>
        </div>
      </Section>
      <Section title="Zones" defaultOpen={false}>
        {ZONE_IDS.map((z) => (
          <div key={z} className={`zone ${zones[z].enabled ? 'on' : ''}`}>
            <Toggle label={ZONE_LABELS[z]} value={zones[z].enabled} onChange={(v) => setZone(z, { enabled: v })} />
            {zones[z].enabled && !master.sync && <ColorPicker value={zones[z].color} onChange={(c) => setZone(z, { color: c }, { transient: true })} onCommit={commit} compact />}
            {zones[z].enabled && <Slider label="Brightness" value={zones[z].brightness} min={0} max={1} onChange={(v) => setZone(z, { brightness: v }, { transient: true })} onCommit={commit} />}
          </div>
        ))}
      </Section>
      <StarlightControls />
      <Section title="Instrument & display themes" defaultOpen={false}>
        <Select<GaugeTheme> label="Gauge cluster theme" value={project.electronics.gaugeTheme} onChange={(v) => setElectronics({ gaugeTheme: v })} options={[{ value: 'tour', label: 'Tour (factory)' }, { value: 'sport', label: 'Sport (factory)' }, { value: 'track', label: 'Track (factory)' }, { value: 'concept_neon', label: 'Neon ring (concept)' }, { value: 'concept_minimal', label: 'Minimal (concept)' }]} />
        <ColorPicker label="Gauge accent / needle color" value={project.electronics.gaugeColor} onChange={(c) => setElectronics({ gaugeColor: c })} compact />
        <Select label="Infotainment theme" value={project.electronics.infotainmentTheme} onChange={(v) => setElectronics({ infotainmentTheme: v })} options={[{ value: 'factory', label: 'MyLink (factory look)' }, { value: 'concept_dark', label: 'Concept dark' }, { value: 'concept_red', label: 'Concept red' }, { value: 'concept_blue', label: 'Concept blue' }]} />
        <Slider label="Display brightness" value={project.electronics.brightness} min={0.2} max={1} onChange={(v) => setElectronics({ brightness: v })} />
        <p className="muted small">Themes marked concept are not factory features.</p>
      </Section>
      <Section title="Saved lighting presets" defaultOpen={false}>
        <div className="row-actions">
          <Button size="sm" icon="save" onClick={async () => { const name = window.prompt('Preset name', 'My lighting'); if (!name) return; const list = (await loadSaved()).filter((p) => p.name !== name); list.push({ name, lighting: project.lighting }); await setSetting('lightingPresets', list); setSaved(list); notify('Lighting preset saved', 'success'); }}>Save current</Button>
        </div>
        {saved?.map((p) => <div key={p.name} className="row-actions"><Button size="sm" onClick={() => updateProject((d) => { d.lighting = JSON.parse(JSON.stringify(p.lighting)); })}>{p.name}</Button><Button size="sm" icon="trash" title="Delete preset" onClick={async () => { const list = (saved ?? []).filter((x) => x.name !== p.name); await setSetting('lightingPresets', list); setSaved(list); }} /></div>)}
        {saved && saved.length === 0 && <p className="muted small">No saved lighting presets yet.</p>}
      </Section>
    </div>
  );
}
