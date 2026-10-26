import { useStore, type Quality } from '../state/store';
import { setSetting } from '../persistence/db';
import { Button, Select, Slider, Toggle } from './common';

export function SettingsPage() {
  const setRoute = useStore((s) => s.setRoute);
  const settings = useStore((s) => s.settings);
  const setSettings = useStore((s) => s.setSettings);
  const update = (patch: Partial<typeof settings>) => { setSettings(patch); void setSetting('settings', { ...settings, ...patch }); };
  return (
    <div className="page narrow">
      <header className="page-head"><Button icon="back" title="Back" onClick={() => setRoute(useStore.getState().project ? 'studio' : 'menu')} /><h2>Settings</h2></header>
      <div className="card form">
        <Select<Quality> label="Render quality" value={settings.quality} onChange={(v) => update({ quality: v })} options={[{ value: 'ultra', label: 'Ultra (1.5x pixels, ambient occlusion, 2K shadows)' }, { value: 'high', label: 'High (1.25x pixels, shadows, antialiasing)' }, { value: 'balanced', label: 'Balanced (1x pixels, shadows)' }, { value: 'mobile', label: 'Mobile (no shadows, fewer lights)' }]} />
        <Slider label="Look sensitivity" value={settings.lookSensitivity} min={0.3} max={2.5} step={0.05} onChange={(v) => update({ lookSensitivity: v })} />
        <Slider label="Movement speed" value={settings.moveSpeed} min={0.4} max={2} step={0.05} onChange={(v) => update({ moveSpeed: v })} />
        <Slider label="Default field of view" value={settings.defaultFov} min={45} max={95} step={1} onChange={(v) => update({ defaultFov: v })} format={(v) => `${v}°`} />
        <Toggle label="Invert vertical look" value={settings.invertY} onChange={(v) => update({ invertY: v })} />
        <Select label="Arrow keys" value={settings.arrowMode} onChange={(v) => update({ arrowMode: v })} options={[{ value: 'look', label: 'Rotate the view' }, { value: 'move', label: 'Move (same as WASD)' }]} />
        <Toggle label="Autosave" value={settings.autosave} onChange={(v) => update({ autosave: v })} hint="Saves about one second after each change" />
        <Toggle label="Reduce motion" value={settings.reduceMotion} onChange={(v) => update({ reduceMotion: v })} />
        <Toggle label="Show hints" value={settings.showHints} onChange={(v) => update({ showHints: v })} />
      </div>
    </div>
  );
}

export function HelpPage() {
  const setRoute = useStore((s) => s.setRoute);
  return (
    <div className="page narrow">
      <header className="page-head"><Button icon="back" title="Back" onClick={() => setRoute(useStore.getState().project ? 'studio' : 'menu')} /><h2>Help &amp; controls</h2></header>
      <div className="card help">
        <h3>Camera</h3>
        <ul>
          <li><kbd>Drag</kbd> look around (mouse or one finger)</li>
          <li><kbd>W A S D</kbd> move · <kbd>E</kbd>/<kbd>Space</kbd> up · <kbd>Q</kbd>/<kbd>C</kbd> down · <kbd>Shift</kbd> faster</li>
          <li><kbd>Arrow keys</kbd> rotate the view (or move, see Settings)</li>
          <li><kbd>Mouse wheel</kbd> zoom (field of view) · <kbd>R</kbd> return to the seat</li>
          <li>Driver / Passenger buttons jump to the seat eye point. Free roam starts as soon as you move. Inspect mode lifts the collision limits for very close looks.</li>
          <li>On phones use the joystick (bottom left) to move and drag anywhere to look.</li>
        </ul>
        <h3>Customizing</h3>
        <ul>
          <li>Click or tap any part of the interior to select it, or pick it from the Parts list. Both stay in sync and the selected part is outlined.</li>
          <li>The inspector shows only the options that apply: material, colors, finish, stitching, text and replacement geometry.</li>
          <li><kbd>Ctrl/⌘ Z</kbd> undo · <kbd>Ctrl/⌘ Shift Z</kbd> or <kbd>Ctrl Y</kbd> redo · <kbd>Ctrl/⌘ S</kbd> save · <kbd>H</kbd> hide interface · <kbd>F</kbd> showroom mode · <kbd>Esc</kbd> deselect</li>
          <li>Seats and doors are linked by default so both sides match. Unlink them in the inspector to design each side separately.</li>
          <li>Compare shows the factory interior next to your design without changing it.</li>
        </ul>
        <h3>Projects</h3>
        <ul>
          <li>Projects autosave to this browser (IndexedDB). Export a JSON backup from the Garage to keep designs across devices.</li>
          <li>Screenshots capture the live 3D scene as PNG.</li>
        </ul>
        <h3>About accuracy</h3>
        <p className="muted">The cockpit is a scripted recreation of the 2019 Stingray 3LT built from published dimensions and reference descriptions, not a scan or a licensed GM model. Corvette emblems are development placeholders. Concept electronics themes are not factory features.</p>
      </div>
    </div>
  );
}
