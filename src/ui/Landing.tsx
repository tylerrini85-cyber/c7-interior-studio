import { useEffect, useState } from 'react';
import { useStore } from '../state/store';
import { listProjects, loadProject } from '../persistence/db';
import { Button, Icon } from './common';

export function Landing() {
  const setRoute = useStore((s) => s.setRoute);
  const loadProjectDoc = useStore((s) => s.loadProjectDoc);
  const notify = useStore((s) => s.notify);
  const [count, setCount] = useState<number | null>(null);
  const [lastId, setLastId] = useState<string | null>(null);
  useEffect(() => { void listProjects().then((p) => { setCount(p.length); setLastId(p[0]?.id ?? null); }).catch(() => setCount(0)); }, []);
  const continueLast = async () => {
    if (!lastId) { notify('No saved project yet. Start a new one.'); return; }
    const doc = await loadProject(lastId); if (doc) loadProjectDoc(doc); else notify('Last project could not be loaded', 'error');
  };
  return (
    <div className="landing">
      <div className="landing-bg" aria-hidden="true"><div className="landing-glow" /><div className="landing-lines" /></div>
      <div className="landing-content">
        <p className="eyebrow">2019 Stingray 3LT · Interior design simulator</p>
        <h1>C7 <span>Interior</span> Studio</h1>
        <p className="lead">Sit inside a recreated Corvette C7 cockpit and redesign every surface in real time: leather, carbon, Alcantara, RGB ambient zones, starlight headliner and replacement parts.</p>
        <nav className="menu" aria-label="Main menu">
          <Button variant="primary" size="lg" icon="plus" onClick={() => setRoute('new')}>New Project</Button>
          <Button variant="outline" size="lg" icon="garage" onClick={() => setRoute('garage')}>My Garage{count ? ` (${count})` : ''}</Button>
          <Button variant="outline" size="lg" icon="play" onClick={() => void continueLast()} disabled={count === 0}>Continue Last Project</Button>
          <Button variant="ghost" size="lg" icon="settings" onClick={() => setRoute('settings')}>Settings</Button>
          <Button variant="ghost" size="lg" icon="help" onClick={() => setRoute('help')}>Help / Controls</Button>
        </nav>
        <p className="footnote"><Icon name="info" size={13} /> Scripted recreation of the C7 cockpit built from published dimensions. Emblems are development placeholders. Projects are stored in this browser.</p>
      </div>
    </div>
  );
}
