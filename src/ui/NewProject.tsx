import { useState } from 'react';
import { useStore } from '../state/store';
import { FACTORY_COLORS } from '../registry/components';
import type { EnvironmentId, FactoryColorId } from '../project/schema';
import { Button, Segmented } from './common';

export function NewProject() {
  const setRoute = useStore((s) => s.setRoute);
  const createProject = useStore((s) => s.createProject);
  const [name, setName] = useState('My C7 Interior');
  const [color, setColor] = useState<FactoryColorId>('jet_black');
  const [seat, setSeat] = useState<'driver' | 'passenger'>('driver');
  const [env, setEnv] = useState<EnvironmentId>('showroom');
  return (
    <div className="page narrow">
      <header className="page-head"><Button icon="back" title="Back" onClick={() => setRoute('menu')} /><h2>New project</h2></header>
      <form className="card form" onSubmit={(e) => { e.preventDefault(); createProject({ name, factoryColor: color, seat, environment: env }); }}>
        <label className="field"><span className="field-label">Project name</span><input value={name} onChange={(e) => setName(e.target.value)} maxLength={48} autoFocus /></label>
        <div className="field"><span className="field-label">Baseline configuration</span>
          <div className="baseline"><strong>2019 Corvette Stingray Coupe · 3LT</strong><span>GT seats · 8-speed automatic · removable roof panel · Napa leather with sueded microfiber upper trim</span></div>
        </div>
        <div className="field"><span className="field-label">Factory interior color</span>
          <div className="color-grid">
            {(Object.keys(FACTORY_COLORS) as FactoryColorId[]).map((id) => (
              <button type="button" key={id} className={`color-card ${color === id ? 'sel' : ''}`} onClick={() => setColor(id)}>
                <span className="chip" style={{ background: FACTORY_COLORS[id].main }} /><span>{FACTORY_COLORS[id].label}</span>
                {(id === 'gray' || id === 'brownstone') && <small>factory-inspired</small>}
              </button>
            ))}
          </div>
        </div>
        <div className="field"><span className="field-label">Starting seat</span><Segmented value={seat} onChange={setSeat} options={[{ value: 'driver', label: 'Driver', icon: 'driver' }, { value: 'passenger', label: 'Passenger', icon: 'passenger' }]} /></div>
        <div className="field"><span className="field-label">Lighting condition</span><Segmented value={env} onChange={setEnv} options={[{ value: 'showroom', label: 'Showroom', icon: 'showroom' }, { value: 'day', label: 'Daylight', icon: 'sun' }, { value: 'sunset', label: 'Sunset', icon: 'sunset' }, { value: 'night', label: 'Night', icon: 'moon' }]} /></div>
        <div className="form-actions"><Button variant="ghost" onClick={() => setRoute('menu')}>Cancel</Button><Button type="submit" variant="primary" icon="play">Enter the cockpit</Button></div>
      </form>
    </div>
  );
}
