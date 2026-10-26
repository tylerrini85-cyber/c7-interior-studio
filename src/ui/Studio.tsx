/** Studio layout: viewport, top bar, parts browser, inspector, lighting panel, camera bar, mobile sheets, overlays. */
import { useEffect, useRef, useState } from 'react';
import { useStore, type CameraMode } from '../state/store';
import { Studio3D } from '../scene/Studio3D';
import { ErrorBoundary } from './ErrorBoundary';
import { CATEGORY_LABELS, CATEGORY_ORDER, COMPONENTS, type Category } from '../registry/components';
import { PRESETS, RANDOM_THEMES, randomizeProject, type RandomTheme } from '../project/presets';
import { exportProjectJson } from '../persistence/db';
import { Inspector } from './Inspector';
import { LightingPanel } from './LightingPanel';
import { Joystick } from './Joystick';
import { Button, Icon, Modal, Segmented, Slider, TextField } from './common';
import { perf } from '../quality/Adaptive';

function useIsMobile() {
  const [m, setM] = useState(() => window.matchMedia('(max-width: 900px)').matches);
  useEffect(() => { const mq = window.matchMedia('(max-width: 900px)'); const f = () => setM(mq.matches); mq.addEventListener('change', f); return () => mq.removeEventListener('change', f); }, []);
  return m;
}

function PartsBrowser() {
  const selected = useStore((s) => s.selected);
  const focusOn = useStore((s) => s.focusOn);
  const hover = useStore((s) => s.hover);
  const [open, setOpen] = useState<Category | null>('steering');
  const [q, setQ] = useState('');
  const filtered = q ? COMPONENTS.filter((c) => (c.label + ' ' + c.group).toLowerCase().includes(q.toLowerCase())) : null;
  return (
    <div className="parts">
      <TextField value={q} onChange={setQ} placeholder="Search parts…" />
      {filtered ? (
        <ul className="part-list">{filtered.map((c) => <li key={c.id}><button type="button" className={selected === c.id ? 'sel' : ''} onClick={() => focusOn(c.id)} onMouseEnter={() => hover(c.id)} onMouseLeave={() => hover(null)}>{c.label}<small>{c.group}</small></button></li>)}</ul>
      ) : CATEGORY_ORDER.map((cat) => {
        const items = COMPONENTS.filter((c) => c.category === cat);
        if (!items.length) return null;
        const isOpen = open === cat || (!!selected && items.some((i) => i.id === selected) && open === null);
        return (
          <div key={cat} className={`cat ${isOpen ? 'open' : ''}`}>
            <button type="button" className="cat-head" onClick={() => setOpen(isOpen ? null : cat)}><Icon name="chevron" size={14} />{CATEGORY_LABELS[cat]}<em>{items.length}</em></button>
            {isOpen && <ul className="part-list">{items.map((c) => <li key={c.id}><button type="button" className={selected === c.id ? 'sel' : ''} onClick={() => focusOn(c.id)} onMouseEnter={() => hover(c.id)} onMouseLeave={() => hover(null)}>{c.label}</button></li>)}</ul>}
          </div>
        );
      })}
    </div>
  );
}

function SaveIndicator() {
  const status = useStore((s) => s.saveStatus);
  const label = { saved: 'Saved', saving: 'Saving…', unsaved: 'Unsaved changes', error: 'Save failed', idle: '' }[status];
  return <span className={`save-status ${status}`} aria-live="polite">{status === 'saved' && <Icon name="check" size={13} />}{label}</span>;
}

function TopBar({ onPresets, onRandom, onExport }: { onPresets: () => void; onRandom: () => void; onExport: () => void }) {
  const project = useStore((s) => s.project)!;
  const setRoute = useStore((s) => s.setRoute);
  const saveNow = useStore((s) => s.saveNow);
  const rename = useStore((s) => s.renameProject);
  const undo = useStore((s) => s.undo); const redo = useStore((s) => s.redo);
  const canUndo = useStore((s) => s.past.length > 0); const canRedo = useStore((s) => s.future.length > 0);
  const compare = useStore((s) => s.compareFactory); const setCompare = useStore((s) => s.setCompareFactory);
  const requestCapture = useStore((s) => s.requestCapture);
  const resetToFactory = useStore((s) => s.resetToFactory);
  const toggleUi = useStore((s) => s.toggleUi);
  const setShowroom = useStore((s) => s.setShowroom);
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(project.name);
  return (
    <header className="topbar">
      <Button icon="garage" title="My Garage" onClick={() => { void saveNow().then(() => setRoute('garage')); }} />
      {editing ? <input className="name-edit" autoFocus value={name} onChange={(e) => setName(e.target.value)} onBlur={() => { rename(name); setEditing(false); }} onKeyDown={(e) => { if (e.key === 'Enter') { rename(name); setEditing(false); } e.stopPropagation(); }} /> : <button type="button" className="project-name" onClick={() => { setName(project.name); setEditing(true); }} title="Rename">{project.name}</button>}
      <SaveIndicator />
      <div className="spacer" />
      <div className="group">
        <Button icon="undo" title="Undo (Ctrl+Z)" onClick={undo} disabled={!canUndo} />
        <Button icon="redo" title="Redo (Ctrl+Shift+Z)" onClick={redo} disabled={!canRedo} />
      </div>
      <div className="group">
        <Button icon="preset" title="Design presets" onClick={onPresets}>Presets</Button>
        <Button icon="dice" title="Random design" onClick={onRandom}>Random</Button>
        <Button icon="compare" title="Compare with factory" active={compare} onClick={() => setCompare(!compare)}>Compare</Button>
        <Button icon="reset" title="Reset everything to factory" onClick={() => { if (window.confirm('Reset the whole interior to the factory configuration? (You can undo this.)')) resetToFactory(); }} />
      </div>
      <div className="group">
        <Button icon="camera" title="Screenshot (PNG)" onClick={() => requestCapture('download')} />
        <Button icon="download" title="Export project file" onClick={onExport} />
        <Button icon="save" title="Save (Ctrl+S)" onClick={() => void saveNow()} />
        <Button icon="eyeOff" title="Hide interface (H)" onClick={() => toggleUi(true)} />
        <Button icon="fullscreen" title="Showroom mode (F)" onClick={() => setShowroom(true)} />
        <Button icon="settings" title="Settings" onClick={() => setRoute('settings')} />
        <Button icon="help" title="Help" onClick={() => setRoute('help')} />
      </div>
    </header>
  );
}

function CameraBar() {
  const mode = useStore((s) => s.cameraMode); const setMode = useStore((s) => s.setCameraMode);
  const resetCamera = useStore((s) => s.resetCamera);
  const project = useStore((s) => s.project)!;
  const updateProject = useStore((s) => s.updateProject);
  const joyPref = useStore((s) => s.joystickVisible); const setJoy = useStore((s) => s.setJoystickVisible);
  const joy = joyPref ?? window.matchMedia('(max-width: 900px)').matches;
  const [moreOpen, setMore] = useState(false);
  const [fps, setFps] = useState(0);
  useEffect(() => { if (!moreOpen) return; const t = setInterval(() => setFps(Math.round(perf.fps)), 1000); return () => clearInterval(t); }, [moreOpen]);
  return (
    <div className="camerabar">
      <Segmented<CameraMode> ariaLabel="Camera" value={mode} onChange={setMode} options={[{ value: 'driver', label: 'Driver seat', icon: 'driver' }, { value: 'passenger', label: 'Passenger seat', icon: 'passenger' }, { value: 'free', label: 'Free roam', icon: 'free' }, { value: 'inspect', label: 'Inspect', icon: 'inspect' }]} />
      <Button icon="reset" title="Reset view (R)" onClick={resetCamera} />
      <Button icon="joystick" title="Toggle joystick" active={joy} onClick={() => setJoy(!joy)} />
      <Button icon="pov" title="View options" active={moreOpen} onClick={() => setMore((o) => !o)} />
      {moreOpen && (
        <div className="camera-more">
          <Slider label="Eye height" value={project.camera.eyeHeight} min={-0.08} max={0.08} step={0.005} onChange={(v) => updateProject((d) => { d.camera.eyeHeight = v; }, { history: false })} format={(v) => `${Math.round(v * 100)} cm`} />
          <Slider label="Field of view" value={project.camera.fov} min={45} max={100} step={1} onChange={(v) => updateProject((d) => { d.camera.fov = v; }, { history: false })} format={(v) => `${v}°`} />
          <Segmented value={project.camera.seat} onChange={(v) => updateProject((d) => { d.camera.seat = v; }, { history: false })} options={[{ value: 'driver', label: 'Default: driver' }, { value: 'passenger', label: 'Default: passenger' }]} />
          <p className="muted small" style={{ marginTop: 8 }}>Renderer: {fps} fps · pixel scale {Math.round(perf.dprScale * 100)}% (adaptive)</p>
        </div>
      )}
    </div>
  );
}

function LoadingOverlay() {
  const loading = useStore((s) => s.loading);
  if (!loading) return null;
  return (
    <div className="loading" role="status">
      <div className="loading-card">
        <h3>{loading.error ? 'Asset failed to load' : 'Preparing the cockpit'}</h3>
        {loading.error ? <p className="error">{loading.error}<br />Check your connection and reload. Your project is safe.</p> : <><div className="bar"><span style={{ width: `${loading.progress}%` }} /></div><p>{loading.label} · {Math.round(loading.progress)}%</p></>}
        {loading.error && <Button variant="primary" onClick={() => window.location.reload()}>Reload</Button>}
      </div>
    </div>
  );
}

function Toast() {
  const toast = useStore((s) => s.toast);
  const [vis, setVis] = useState(false);
  useEffect(() => { if (!toast) return; setVis(true); const t = setTimeout(() => setVis(false), 2800); return () => clearTimeout(t); }, [toast]);
  if (!toast || !vis) return null;
  return <div className={`toast ${toast.kind}`} role="status">{toast.text}</div>;
}

function Hints() {
  const show = useStore((s) => s.settings.showHints);
  const [dismissed, setDismissed] = useState(false);
  if (!show || dismissed) return null;
  return <div className="hint"><span>Drag to look · WASD to move · click any part to customize · H hides the interface</span><button type="button" onClick={() => setDismissed(true)} aria-label="Dismiss hint"><Icon name="close" size={14} /></button></div>;
}

export function Studio() {
  const project = useStore((s) => s.project);
  const uiHidden = useStore((s) => s.uiHidden); const toggleUi = useStore((s) => s.toggleUi);
  const showroom = useStore((s) => s.showroom); const setShowroom = useStore((s) => s.setShowroom);
  const panel = useStore((s) => s.panel); const setPanel = useStore((s) => s.setPanel);
  const sheet = useStore((s) => s.mobileSheet); const setSheet = useStore((s) => s.setMobileSheet);
  const joyPref = useStore((s) => s.joystickVisible);
  const compareImages = useStore((s) => s.compareImages); const setCompareImages = useStore((s) => s.setCompareImages);
  const requestCapture = useStore((s) => s.requestCapture);
  const updateProject = useStore((s) => s.updateProject);
  const notify = useStore((s) => s.notify);
  const selected = useStore((s) => s.selected);
  const compare = useStore((s) => s.compareFactory);
  const isMobile = useIsMobile();
  const [presetsOpen, setPresets] = useState(false);
  const [randomOpen, setRandom] = useState(false);
  const [leftOpen, setLeft] = useState(true);
  const thumbTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // thumbnails: capture shortly after changes settle
  const updatedAt = project?.updatedAt;
  useEffect(() => { if (!updatedAt) return; if (thumbTimer.current) clearTimeout(thumbTimer.current); thumbTimer.current = setTimeout(() => requestCapture('thumbnail'), 2500); return () => { if (thumbTimer.current) clearTimeout(thumbTimer.current); }; }, [updatedAt, requestCapture]);

  // keyboard shortcuts
  useEffect(() => {
    const k = (e: KeyboardEvent) => {
      const el = document.activeElement as HTMLElement | null;
      if (el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT' || el.isContentEditable)) return;
      const s = useStore.getState();
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.code === 'KeyZ') { e.preventDefault(); if (e.shiftKey) s.redo(); else s.undo(); }
      else if (mod && e.code === 'KeyY') { e.preventDefault(); s.redo(); }
      else if (mod && e.code === 'KeyS') { e.preventDefault(); void s.saveNow(); }
      else if (e.code === 'KeyH' && !mod) { s.toggleUi(); if (s.showroom) s.setShowroom(false); }
      else if (e.code === 'KeyF' && !mod) { s.setShowroom(!s.showroom); }
      else if (e.code === 'Escape') { if (s.showroom) s.setShowroom(false); else if (s.uiHidden) s.toggleUi(false); else s.select(null); }
      else if (e.code === 'KeyP' && !mod) { s.requestCapture('download'); }
    };
    window.addEventListener('keydown', k); return () => window.removeEventListener('keydown', k);
  }, []);

  useEffect(() => { if (isMobile && selected) setSheet('inspector'); // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected, isMobile]);

  if (!project) return null;
  const exportJson = () => { const blob = new Blob([exportProjectJson(project)], { type: 'application/json' }); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `${project.name.replace(/[^a-z0-9-_]+/gi, '_')}.c7studio.json`; a.click(); URL.revokeObjectURL(a.href); notify('Project exported', 'success'); };
  const applyPreset = (id: string) => { const p = PRESETS.find((x) => x.id === id); if (!p) return; updateProject((d) => p.apply(d)); setPresets(false); notify(`Applied "${p.name}"`, 'success'); };
  const applyRandom = (t: RandomTheme) => { updateProject((d) => randomizeProject(d, t)); setRandom(false); notify('Random design generated. Undo to go back.', 'success'); };

  return (
    <div className={`studio ${uiHidden ? 'ui-hidden' : ''} ${isMobile ? 'mobile' : ''}`}>
      <div className="viewport"><ErrorBoundary><Studio3D /></ErrorBoundary></div>
      {!uiHidden && !isMobile && (
        <>
          <TopBar onPresets={() => setPresets(true)} onRandom={() => setRandom(true)} onExport={exportJson} />
          <aside className={`left ${leftOpen ? '' : 'collapsed'}`}>
            <div className="panel-tabs">
              <button type="button" className={panel === 'parts' ? 'is-active' : ''} onClick={() => { setPanel('parts'); setLeft(true); }}>Parts</button>
              <button type="button" className={panel === 'lighting' ? 'is-active' : ''} onClick={() => { setPanel('lighting'); setLeft(true); }}>Lighting</button>
              <button type="button" className="collapse" onClick={() => setLeft((o) => !o)} aria-label="Collapse panel"><Icon name={leftOpen ? 'back' : 'chevron'} size={14} /></button>
            </div>
            {leftOpen && <div className="panel-body">{panel === 'lighting' ? <LightingPanel /> : <PartsBrowser />}</div>}
          </aside>
          <aside className="right"><div className="panel-body"><Inspector /></div></aside>
          <footer className="bottombar"><CameraBar /></footer>
          <Hints />
        </>
      )}
      {!uiHidden && isMobile && (
        <>
          <header className="topbar mobile">
            <Button icon="garage" title="Garage" onClick={() => { void useStore.getState().saveNow().then(() => useStore.getState().setRoute('garage')); }} />
            <span className="project-name">{project.name}</span><SaveIndicator /><div className="spacer" />
            <Button icon="undo" title="Undo" onClick={() => useStore.getState().undo()} /><Button icon="redo" title="Redo" onClick={() => useStore.getState().redo()} />
            <Button icon="eyeOff" title="Hide UI" onClick={() => toggleUi(true)} />
          </header>
          <div className="mobile-fabs">
            <Button icon="parts" title="Parts" active={sheet === 'parts'} onClick={() => setSheet(sheet === 'parts' ? 'none' : 'parts')} />
            <Button icon="lighting" title="Lighting" active={sheet === 'lighting'} onClick={() => setSheet(sheet === 'lighting' ? 'none' : 'lighting')} />
            <Button icon="camera" title="Camera" active={sheet === 'camera'} onClick={() => setSheet(sheet === 'camera' ? 'none' : 'camera')} />
            <Button icon="preset" title="Presets" onClick={() => setPresets(true)} />
            <Button icon="dice" title="Random" onClick={() => setRandom(true)} />
            <Button icon="compare" title="Compare" active={compare} onClick={() => useStore.getState().setCompareFactory(!compare)} />
            <Button icon="download" title="Screenshot" onClick={() => requestCapture('download')} />
          </div>
          <div className="seat-fabs">
            <Button icon="driver" title="Driver seat" onClick={() => useStore.getState().setCameraMode('driver')} />
            <Button icon="passenger" title="Passenger seat" onClick={() => useStore.getState().setCameraMode('passenger')} />
          </div>
          {sheet !== 'none' && (
            <div className="sheet">
              <div className="sheet-handle" onClick={() => setSheet('none')}><span /></div>
              <div className="sheet-body">
                {sheet === 'parts' && <PartsBrowser />}
                {sheet === 'inspector' && <Inspector />}
                {sheet === 'lighting' && <LightingPanel />}
                {sheet === 'camera' && <CameraBar />}
              </div>
            </div>
          )}
        </>
      )}
      {(joyPref ?? (isMobile || ('ontouchstart' in window))) && !showroom && <Joystick />}
      {uiHidden && <button type="button" className="show-ui" onClick={() => { toggleUi(false); setShowroom(false); }} title="Show interface (H)"><Icon name="eye" /></button>}
      {compare && !uiHidden && <div className="compare-badge"><Icon name="compare" size={14} /> Showing factory interior · <button type="button" onClick={() => requestCapture('compare')}>side-by-side</button> · <button type="button" onClick={() => useStore.getState().setCompareFactory(false)}>back to my design</button></div>}
      <LoadingOverlay />
      <Toast />
      {presetsOpen && (
        <Modal title="Design presets" onClose={() => setPresets(false)} wide>
          <div className="preset-grid">{PRESETS.map((p) => <button type="button" key={p.id} className="preset-card" onClick={() => applyPreset(p.id)}><strong>{p.name}</strong><span>{p.description}</span></button>)}</div>
          <p className="muted small">Presets replace the current part settings (undo restores your design).</p>
        </Modal>
      )}
      {randomOpen && (
        <Modal title="Random design generator" onClose={() => setRandom(false)}>
          <div className="preset-grid">{RANDOM_THEMES.map((t) => <button type="button" key={t.id} className="preset-card" onClick={() => applyRandom(t.id)}><strong>{t.label}</strong><span>Compatible materials, colors, parts and lighting for this theme</span></button>)}</div>
        </Modal>
      )}
      {compareImages && (
        <Modal title="Before / after" onClose={() => setCompareImages(null)} wide>
          <div className="compare-grid"><figure><img src={compareImages.before} alt="Factory interior" /><figcaption>Factory</figcaption></figure><figure><img src={compareImages.after} alt="Custom interior" /><figcaption>{project.name}</figcaption></figure></div>
          <div className="form-actions"><Button icon="download" variant="primary" onClick={() => { const c = document.createElement('canvas'); const a = new Image(), b = new Image(); let n = 0; const done = () => { if (++n < 2) return; c.width = a.width + b.width + 8; c.height = Math.max(a.height, b.height); const ctx = c.getContext('2d')!; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, c.width, c.height); ctx.drawImage(a, 0, 0); ctx.drawImage(b, a.width + 8, 0); const l = document.createElement('a'); l.href = c.toDataURL('image/png'); l.download = `${project.name.replace(/[^a-z0-9-_]+/gi, '_')}-before-after.png`; l.click(); }; a.onload = done; b.onload = done; a.src = compareImages.before; b.src = compareImages.after; }}>Export before/after PNG</Button></div>
        </Modal>
      )}
    </div>
  );
}
