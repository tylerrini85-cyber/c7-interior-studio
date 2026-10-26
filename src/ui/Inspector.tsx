/** Context-sensitive customization inspector for the selected component. */
import { useStore } from '../state/store';
import { COMPONENT_MAP, VARIANTS, type VariantSlot } from '../registry/components';
import { MATERIAL_GROUPS, MATERIAL_PRESETS } from '../materials/engine';
import type { Finish, MaterialKind, StitchPattern } from '../project/schema';
import { Button, ColorPicker, Section, Segmented, Select, TextField, Toggle } from './common';

const PROFANITY = /\b(fuck|shit|bitch|cunt|nigg|fag)\w*/i;

export function Inspector() {
  const selected = useStore((s) => s.selected);
  const project = useStore((s) => s.project);
  const setPart = useStore((s) => s.setPart);
  const commit = useStore((s) => s.commitTransient);
  const resetPart = useStore((s) => s.resetPartToFactory);
  const select = useStore((s) => s.select);
  const updateProject = useStore((s) => s.updateProject);
  const setVariant = useStore((s) => s.setVariant);
  const notify = useStore((s) => s.notify);
  if (!project) return null;
  if (!selected) return <div className="inspector-empty"><p>Click a part of the interior, or choose one from the Parts list, to customize it.</p></div>;
  const def = COMPONENT_MAP.get(selected);
  const cfg = project.parts[selected];
  if (!def || !cfg) return null;
  const caps = def.caps;
  const allowed = caps.materials;
  const groups = MATERIAL_GROUPS.filter((g) => allowed.some((m) => MATERIAL_PRESETS[m].group === g));
  const slot: VariantSlot | undefined = caps.variantSlot;
  const variantOwner = slot ? (slot === 'steering' ? 'steering.rim.upper' : slot === 'shifter' ? 'console.shifter' : `${slot}.headrest`) : null;
  const currentVariant = variantOwner ? project.parts[variantOwner]?.variant ?? VARIANTS[slot!][0].id : null;
  const linked = selected.startsWith('seats.') ? project.linkSeats : selected.startsWith('doors.') ? project.linkDoors : null;

  return (
    <div className="inspector">
      <header className="inspector-head">
        <div><p className="eyebrow">{def.group}</p><h3>{def.label}</h3></div>
        <Button icon="close" title="Deselect" onClick={() => select(null)} />
      </header>
      {linked !== null && (
        <Toggle label={selected.startsWith('seats.') ? 'Link both seats' : 'Link both doors'} value={linked} hint="Changes apply to both sides" onChange={(v) => updateProject((d) => { if (selected.startsWith('seats.')) d.linkSeats = v; else d.linkDoors = v; }, { history: false })} />
      )}
      {slot && (
        <Section title="Shape / replacement part">
          <div className="variant-list">
            {VARIANTS[slot].map((v) => (
              <button type="button" key={v.id} className={`variant ${currentVariant === v.id ? 'sel' : ''}`} onClick={() => setVariant(slot, v.id)}>
                <strong>{v.label}</strong><span>{v.description}</span>
              </button>
            ))}
          </div>
          {slot === 'shifter' && <p className="muted small">Manual shifters are concept replacements; the baseline car is an 8-speed automatic.</p>}
        </Section>
      )}
      <Section title="Material">
        <div className="material-groups">
          {groups.map((g) => (
            <div key={g} className="material-group">
              <span className="group-label">{g}</span>
              <div className="material-chips">
                {allowed.filter((m) => MATERIAL_PRESETS[m].group === g).map((m) => (
                  <button type="button" key={m} className={`chip-btn ${cfg.material === m ? 'sel' : ''}`} onClick={() => setPart(selected, { material: m as MaterialKind })}>{MATERIAL_PRESETS[m].label}</button>
                ))}
              </div>
            </div>
          ))}
        </div>
        {caps.finish !== false && (
          <Segmented<Finish> ariaLabel="Surface finish" value={cfg.finish ?? 'satin'} onChange={(f) => setPart(selected, { finish: f })} options={[{ value: 'matte', label: 'Matte' }, { value: 'satin', label: 'Satin' }, { value: 'gloss', label: 'Gloss' }]} />
        )}
      </Section>
      <Section title="Colors">
        <ColorPicker label={MATERIAL_PRESETS[cfg.material].group === 'Carbon fiber' ? 'Weave tint' : 'Base color'} value={cfg.color} onChange={(c) => setPart(selected, { color: c }, { transient: true })} onCommit={commit} compact />
        {caps.color2 && <ColorPicker label="Secondary color (two-tone)" value={cfg.color2 ?? cfg.color} onChange={(c) => setPart(selected, { color2: c }, { transient: true })} onCommit={commit} compact />}
        {caps.accent && <ColorPicker label="Accent color" value={cfg.accent ?? cfg.color} onChange={(c) => setPart(selected, { accent: c }, { transient: true })} onCommit={commit} compact />}
      </Section>
      {caps.stitch && (
        <Section title="Stitching">
          <Select<StitchPattern> label="Pattern" value={cfg.stitch?.pattern ?? 'none'} onChange={(p) => setPart(selected, { stitch: { color: cfg.stitch?.color ?? '#9a9a9e', pattern: p } })} options={[{ value: 'none', label: 'None' }, { value: 'single', label: 'Single row' }, { value: 'double', label: 'Double row' }, { value: 'pleat', label: 'Horizontal pleats' }, { value: 'diamond', label: 'Diamond' }, { value: 'hex', label: 'Hexagon quilt' }]} />
          {cfg.stitch && cfg.stitch.pattern !== 'none' && <ColorPicker label="Thread color" value={cfg.stitch.color} onChange={(c) => setPart(selected, { stitch: { pattern: cfg.stitch!.pattern, color: c } }, { transient: true })} onCommit={commit} compact />}
        </Section>
      )}
      {caps.text && (
        <Section title="Custom text / embroidery">
          <TextField label="Text" value={cfg.text ?? ''} maxLength={16} placeholder="e.g. initials" onChange={(t) => { if (PROFANITY.test(t)) { notify('That text is not allowed', 'error'); return; } setPart(selected, { text: t }, { transient: true }); }} onCommit={commit} />
          <ColorPicker label="Thread color" value={cfg.textColor ?? '#c0c0c4'} onChange={(c) => setPart(selected, { textColor: c }, { transient: true })} onCommit={commit} compact />
          <p className="muted small">The factory emblem on this part is a development placeholder; licensed artwork can be dropped in later.</p>
        </Section>
      )}
      <div className="inspector-actions">
        <Button icon="reset" onClick={() => resetPart(selected)}>Reset this part to factory</Button>
      </div>
    </div>
  );
}
