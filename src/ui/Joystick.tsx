/** Semi-transparent virtual joystick for touch movement; writes into the shared joystick state read by the camera rig. */
import { useRef } from 'react';
import { joystick } from '../camera/Rig';

export function Joystick() {
  const base = useRef<HTMLDivElement>(null);
  const knob = useRef<HTMLDivElement>(null);
  const start = (e: React.PointerEvent) => {
    const el = base.current!; el.setPointerCapture(e.pointerId);
    const rect = el.getBoundingClientRect(); const cx = rect.left + rect.width / 2, cy = rect.top + rect.height / 2; const R = rect.width / 2 - 14;
    const move = (ev: PointerEvent) => {
      let dx = ev.clientX - cx, dy = ev.clientY - cy; const d = Math.hypot(dx, dy); if (d > R) { dx *= R / d; dy *= R / d; }
      joystick.x = dx / R; joystick.y = dy / R; joystick.active = true;
      if (knob.current) knob.current.style.transform = `translate(${dx}px, ${dy}px)`;
    };
    const up = () => { joystick.x = 0; joystick.y = 0; joystick.active = false; if (knob.current) knob.current.style.transform = ''; el.removeEventListener('pointermove', move); el.removeEventListener('pointerup', up); el.removeEventListener('pointercancel', up); };
    el.addEventListener('pointermove', move); el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
    move(e.nativeEvent);
  };
  return (
    <div ref={base} className="joystick" onPointerDown={start} aria-label="Movement joystick" role="application">
      <div ref={knob} className="joystick-knob" />
    </div>
  );
}
