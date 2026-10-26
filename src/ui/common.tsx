/** Shared UI primitives: buttons, sliders, color picker, selects, toggles, modal, toast, icons. */
import { useEffect, useRef, useState, type ReactNode } from 'react';

export const Icon = ({ name, size = 18 }: { name: string; size?: number }) => {
  const paths: Record<string, ReactNode> = {
    driver: <><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="2.5" /><path d="M12 3v6.5M12 14.5V21M4.5 15l6-2M19.5 15l-6-2" /></>,
    passenger: <><path d="M6 20v-6a6 6 0 0 1 12 0v6" /><circle cx="12" cy="7" r="3" /></>,
    free: <><path d="M12 2v4M12 18v4M2 12h4M18 12h4" /><circle cx="12" cy="12" r="4" /></>,
    inspect: <><circle cx="11" cy="11" r="7" /><path d="M21 21l-4.5-4.5M11 8v6M8 11h6" /></>,
    reset: <><path d="M3 12a9 9 0 1 0 3-6.7" /><path d="M3 4v5h5" /></>,
    undo: <><path d="M9 14l-4-4 4-4" /><path d="M5 10h9a5 5 0 0 1 0 10h-2" /></>,
    redo: <><path d="M15 14l4-4-4-4" /><path d="M19 10h-9a5 5 0 0 0 0 10h2" /></>,
    camera: <><path d="M4 8h3l2-3h6l2 3h3v11H4z" /><circle cx="12" cy="13" r="3.5" /></>,
    eye: <><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z" /><circle cx="12" cy="12" r="3" /></>,
    eyeOff: <><path d="M3 3l18 18M10.6 10.6a3 3 0 0 0 4.2 4.2M9.9 5.2A10.5 10.5 0 0 1 12 5c6 0 10 7 10 7a17 17 0 0 1-3.4 4.2M6.6 6.6A17 17 0 0 0 2 12s4 7 10 7a10 10 0 0 0 4.4-1" /></>,
    sun: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></>,
    sunset: <><path d="M3 18h18M5 14a7 7 0 0 1 14 0" /><path d="M12 4v3M4 11l2 1M20 11l-2 1" /></>,
    moon: <><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z" /></>,
    showroom: <><path d="M3 20h18M5 20V8l7-4 7 4v12" /><path d="M9 20v-6h6v6" /></>,
    lighting: <><path d="M9 18h6M10 21h4" /><path d="M12 3a6 6 0 0 0-4 10.5c.8.8 1 1.5 1 2.5h6c0-1 .2-1.7 1-2.5A6 6 0 0 0 12 3z" /></>,
    star: <><path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z" /></>,
    parts: <><path d="M4 6h16M4 12h16M4 18h16" /></>,
    close: <><path d="M6 6l12 12M18 6L6 18" /></>,
    back: <><path d="M15 5l-7 7 7 7" /></>,
    plus: <><path d="M12 5v14M5 12h14" /></>,
    save: <><path d="M5 3h11l3 3v15H5z" /><path d="M8 3v6h8V3M8 21v-7h8v7" /></>,
    garage: <><path d="M3 10l9-6 9 6v11H3z" /><path d="M7 21v-8h10v8" /></>,
    settings: <><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" /></>,
    help: <><circle cx="12" cy="12" r="9" /><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .9-1 1.7M12 17h0" /></>,
    compare: <><path d="M12 3v18M4 7h5v10H4zM15 7h5v10h-5z" /></>,
    dice: <><rect x="4" y="4" width="16" height="16" rx="3" /><circle cx="9" cy="9" r="1" /><circle cx="15" cy="15" r="1" /><circle cx="15" cy="9" r="1" /><circle cx="9" cy="15" r="1" /></>,
    preset: <><path d="M4 5h16v4H4zM4 11h10v4H4zM4 17h7v2H4z" /></>,
    fullscreen: <><path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5" /></>,
    download: <><path d="M12 3v12M7 10l5 5 5-5M4 21h16" /></>,
    upload: <><path d="M12 21V9M7 14l5-5 5 5M4 3h16" /></>,
    copy: <><rect x="9" y="9" width="11" height="11" rx="2" /><path d="M5 15V5a2 2 0 0 1 2-2h10" /></>,
    trash: <><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13" /></>,
    edit: <><path d="M4 20h4l10-10-4-4L4 16z" /><path d="M13 7l4 4" /></>,
    link: <><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1" /><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1" /></>,
    joystick: <><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="3" /></>,
    chevron: <><path d="M9 6l6 6-6 6" /></>,
    check: <><path d="M5 12l5 5L20 7" /></>,
    info: <><circle cx="12" cy="12" r="9" /><path d="M12 8h0M12 11v6" /></>,
    menu: <><path d="M4 7h16M4 12h16M4 17h16" /></>,
    play: <><path d="M7 5v14l11-7z" /></>,
    pov: <><path d="M3 12c3-5 6-7 9-7s6 2 9 7c-3 5-6 7-9 7s-6-2-9-7z" /><circle cx="12" cy="12" r="2.5" /></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] ?? <circle cx="12" cy="12" r="8" />}</svg>;
};

export function Button({ children, onClick, variant = 'ghost', icon, active, title, disabled, className = '', type = 'button', size = 'md' }: { children?: ReactNode; onClick?: () => void; variant?: 'primary' | 'ghost' | 'outline' | 'danger' | 'subtle'; icon?: string; active?: boolean; title?: string; disabled?: boolean; className?: string; type?: 'button' | 'submit'; size?: 'sm' | 'md' | 'lg' }) {
  return (
    <button type={type} className={`btn btn-${variant} btn-${size} ${active ? 'is-active' : ''} ${className}`} onClick={onClick} title={title} aria-label={title} disabled={disabled} aria-pressed={active}>
      {icon && <Icon name={icon} size={size === 'sm' ? 15 : 18} />}
      {children && <span>{children}</span>}
    </button>
  );
}

export function Slider({ label, value, min, max, step = 0.01, onChange, onCommit, format }: { label?: string; value: number; min: number; max: number; step?: number; onChange: (v: number) => void; onCommit?: () => void; format?: (v: number) => string }) {
  return (
    <label className="field slider">
      {label && <span className="field-label">{label}<em>{format ? format(value) : Math.round(value * 100) / 100}</em></span>}
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(parseFloat(e.target.value))} onPointerUp={onCommit} onKeyUp={onCommit} onBlur={onCommit} />
    </label>
  );
}

export function Toggle({ label, value, onChange, hint }: { label: string; value: boolean; onChange: (v: boolean) => void; hint?: string }) {
  return (
    <label className="field toggle">
      <span className="field-label">{label}{hint && <small>{hint}</small>}</span>
      <button type="button" role="switch" aria-checked={value} className={`switch ${value ? 'on' : ''}`} onClick={() => onChange(!value)}><span /></button>
    </label>
  );
}

export function Select<T extends string>({ label, value, options, onChange }: { label?: string; value: T; options: { value: T; label: string }[]; onChange: (v: T) => void }) {
  return (
    <label className="field">
      {label && <span className="field-label">{label}</span>}
      <select value={value} onChange={(e) => onChange(e.target.value as T)}>
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </label>
  );
}

export function TextField({ label, value, onChange, placeholder, maxLength = 40, onCommit }: { label?: string; value: string; onChange: (v: string) => void; placeholder?: string; maxLength?: number; onCommit?: () => void }) {
  return (
    <label className="field">
      {label && <span className="field-label">{label}</span>}
      <input type="text" value={value} maxLength={maxLength} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} onBlur={onCommit} onKeyDown={(e) => { if (e.key === 'Enter') onCommit?.(); e.stopPropagation(); }} />
    </label>
  );
}

const PRESET_COLORS = ['#141416', '#0d0d0f', '#2a2a2e', '#5c5e61', '#8d9096', '#c9ccd2', '#f5f5f7', '#6a1116', '#b3161c', '#ff1e1e', '#ff5a1f', '#ffb300', '#ffd400', '#1b5e20', '#00c2a8', '#0f1a33', '#1f3a7a', '#3d7bff', '#00e5ff', '#2b0a3d', '#b26bff', '#ff2d95', '#a98a62', '#4a3024', '#d4af37'];

function hexToRgb(hex: string): [number, number, number] { const h = hex.replace('#', ''); const n = parseInt(h.length === 3 ? h.split('').map((c) => c + c).join('') : h, 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
function rgbToHex(r: number, g: number, b: number) { return '#' + [r, g, b].map((v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')).join(''); }
function hexToHsv(hex: string) { const [r, g, b] = hexToRgb(hex).map((v) => v / 255); const max = Math.max(r, g, b), min = Math.min(r, g, b); const d = max - min; let h = 0; if (d) { if (max === r) h = ((g - b) / d) % 6; else if (max === g) h = (b - r) / d + 2; else h = (r - g) / d + 4; h *= 60; if (h < 0) h += 360; } return { h, s: max ? d / max : 0, v: max }; }
function hsvToHex(h: number, s: number, v: number) { const c = v * s; const x = c * (1 - Math.abs(((h / 60) % 2) - 1)); const m = v - c; let r = 0, g = 0, b = 0; if (h < 60) [r, g, b] = [c, x, 0]; else if (h < 120) [r, g, b] = [x, c, 0]; else if (h < 180) [r, g, b] = [0, c, x]; else if (h < 240) [r, g, b] = [0, x, c]; else if (h < 300) [r, g, b] = [x, 0, c]; else [r, g, b] = [c, 0, x]; return rgbToHex((r + m) * 255, (g + m) * 255, (b + m) * 255); }

/** Full color picker: saturation/value square, hue bar, hex and RGB inputs, swatches. */
export function ColorPicker({ label, value, onChange, onCommit, compact }: { label?: string; value: string; onChange: (hex: string) => void; onCommit?: () => void; compact?: boolean }) {
  const [open, setOpen] = useState(!compact);
  const hsv = hexToHsv(value);
  const hueRef = useRef(hsv.h);
  if (hsv.s > 0.02 && hsv.v > 0.02) hueRef.current = hsv.h;
  const h = hueRef.current;
  const [r, g, b] = hexToRgb(value);
  const sq = useRef<HTMLDivElement>(null);
  const drag = (e: React.PointerEvent, fn: (x: number, y: number) => void) => {
    const el = e.currentTarget as HTMLElement; el.setPointerCapture(e.pointerId);
    const move = (ev: PointerEvent) => { const rct = el.getBoundingClientRect(); fn(Math.max(0, Math.min(1, (ev.clientX - rct.left) / rct.width)), Math.max(0, Math.min(1, (ev.clientY - rct.top) / rct.height))); };
    move(e.nativeEvent);
    const up = () => { el.removeEventListener('pointermove', move); el.removeEventListener('pointerup', up); onCommit?.(); };
    el.addEventListener('pointermove', move); el.addEventListener('pointerup', up);
  };
  return (
    <div className="field colorpicker">
      {label && <span className="field-label">{label}</span>}
      <div className="cp-row">
        <button type="button" className="swatch" style={{ background: value }} onClick={() => setOpen((o) => !o)} aria-label="Toggle color picker" />
        <input className="hex" type="text" value={value} onChange={(e) => { const v = e.target.value; if (/^#[0-9a-fA-F]{6}$/.test(v)) { onChange(v); onCommit?.(); } }} onKeyDown={(e) => e.stopPropagation()} aria-label="Hex color" />
        <div className="rgb">
          {(['R', 'G', 'B'] as const).map((ch, i) => <input key={ch} type="number" min={0} max={255} value={[r, g, b][i]} aria-label={ch} onChange={(e) => { const arr = [r, g, b]; arr[i] = parseInt(e.target.value || '0'); onChange(rgbToHex(arr[0], arr[1], arr[2])); }} onBlur={onCommit} onKeyDown={(e) => e.stopPropagation()} />)}
        </div>
      </div>
      {open && (
        <div className="cp-body">
          <div ref={sq} className="cp-square" style={{ background: `linear-gradient(to top, #000, transparent), linear-gradient(to right, #fff, hsl(${h}, 100%, 50%))` }} onPointerDown={(e) => drag(e, (x, y) => onChange(hsvToHex(h, x, 1 - y)))}>
            <span className="cp-cursor" style={{ left: `${hsv.s * 100}%`, top: `${(1 - hsv.v) * 100}%` }} />
          </div>
          <div className="cp-hue" onPointerDown={(e) => drag(e, (x) => { hueRef.current = x * 360; onChange(hsvToHex(x * 360, Math.max(hsv.s, 0.6), Math.max(hsv.v, 0.5))); })}>
            <span className="cp-cursor" style={{ left: `${(h / 360) * 100}%` }} />
          </div>
          <div className="cp-swatches">
            {PRESET_COLORS.map((c) => <button type="button" key={c} className={`mini-swatch ${c === value ? 'sel' : ''}`} style={{ background: c }} onClick={() => { onChange(c); onCommit?.(); }} aria-label={c} />)}
          </div>
        </div>
      )}
    </div>
  );
}

export function Modal({ title, onClose, children, wide }: { title: string; onClose: () => void; children: ReactNode; wide?: boolean }) {
  useEffect(() => { const k = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); }; window.addEventListener('keydown', k); return () => window.removeEventListener('keydown', k); }, [onClose]);
  return (
    <div className="modal-backdrop" onClick={onClose} role="dialog" aria-modal="true" aria-label={title}>
      <div className={`modal ${wide ? 'wide' : ''}`} onClick={(e) => e.stopPropagation()}>
        <header><h3>{title}</h3><Button icon="close" title="Close" onClick={onClose} /></header>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}

export function Section({ title, children, defaultOpen = true, right }: { title: string; children: ReactNode; defaultOpen?: boolean; right?: ReactNode }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <section className={`section ${open ? 'open' : ''}`}>
      <header onClick={() => setOpen((o) => !o)}><Icon name="chevron" size={14} /><h4>{title}</h4>{right && <span onClick={(e) => e.stopPropagation()}>{right}</span>}</header>
      {open && <div className="section-body">{children}</div>}
    </section>
  );
}

export function Segmented<T extends string>({ value, options, onChange, ariaLabel }: { value: T; options: { value: T; label: string; icon?: string }[]; onChange: (v: T) => void; ariaLabel?: string }) {
  return (
    <div className="segmented" role="group" aria-label={ariaLabel}>
      {options.map((o) => <button type="button" key={o.value} className={o.value === value ? 'is-active' : ''} onClick={() => onChange(o.value)} aria-pressed={o.value === value}>{o.icon && <Icon name={o.icon} size={15} />}<span>{o.label}</span></button>)}
    </div>
  );
}
