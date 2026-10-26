"""Seats. Factory GT seat (baseline): one-piece hooded backrest with integrated headrest, stitched headrest pad with
the flags badge, pass-through slot, wide perforated centre inserts, deep wrapped bolsters, plastic back shell, outboard
switch trim, seatbelt (IMG_4500 / 4507 / 4497 / 4513 / 4503 / 4504). Variants: competition (deeper bolsters, harness
slots), racing_shell (fixed-back carbon bucket)."""
import math
from mathutils import Vector
import lib
import layout as L

VARIANTS = ['gt', 'competition', 'racing_shell']

BACK_H = 0.78            # hinge to the top of the integrated headrest along the recline axis
SLOT_S = 0.745           # pass-through slot centre (fraction of BACK_H)
PAD_S0, PAD_S1 = 0.80, 0.975   # headrest pad extent


def _sm(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def _gauss(x, c, w):
    return math.exp(-((x - c) / w) ** 2)


# ---------------------------------------------------------------------------
# backrest surface
# ---------------------------------------------------------------------------
def back_half_w(s, variant):
    """Half width of the backrest outline at fraction s of BACK_H (wide shoulders, tapering hooded top)."""
    base = 0.25 + 0.02 * _sm(0.25, 0.55, s) * (1 - _sm(0.55, 0.62, s))      # shoulder flare peaks ~55 %
    base = 0.25 + 0.022 * _gauss(s, 0.52, 0.16)
    taper = _sm(0.62, 1.0, s)
    hw = base - 0.14 * taper                                                   # 0.27 -> ~0.12 at the top
    hw -= 0.035 * _sm(0.95, 1.0, s)                                           # rounded crown
    if variant != 'gt':
        hw += 0.01 * (1 - taper)
    return hw


def back_center_depth(s, variant):
    """Forward depth (along fwd) of the backrest centre line: lumbar push, shoulder recess, headrest coming forward."""
    d = 0.062 + 0.035 * _gauss(s, 0.27, 0.17) - 0.03 * _sm(0.45, 0.72, s)
    d += 0.055 * _sm(0.74, 0.86, s)                                           # headrest region sits forward again
    d -= 0.03 * _sm(0.95, 1.0, s)
    return d


def back_bolster(s, x, hw, variant):
    """Side-bolster bulge at lateral x (relative to the seat centre)."""
    amp = {'gt': 0.105, 'competition': 0.13, 'racing_shell': 0.14}[variant]
    env = math.sin(math.pi * max(0.0, min(1.0, s / 0.80))) if s < 0.80 else 0.0
    env = env ** 0.7
    env *= 1.0 + 0.25 * _gauss(s, 0.62, 0.12)                                  # shoulder wings reach furthest forward
    peak = hw - 0.07
    u = (abs(x) - peak) / 0.085
    shape = max(0.0, 1.0 - u * u)
    inner = _sm(hw - 0.20, hw - 0.12, abs(x))
    # the centre is a shallow trough between the pads (bucket feel)
    trough = -0.014 * max(0.0, 1.0 - (abs(x) / max(0.05, hw - 0.12)) ** 2) * (env if s < 0.80 else 0.0)
    return amp * env * shape * inner + trough


def back_front(s, x, variant):
    hw = back_half_w(s, variant)
    return back_center_depth(s, variant) + back_bolster(s, x, hw, variant)


def _back_frame():
    hinge = Vector((0.0, L.CUSHION_Y0 + 0.02, L.CUSHION_TOP_Z - 0.02))
    up = Vector((0, -math.sin(L.SEATBACK_RECLINE), math.cos(L.SEATBACK_RECLINE)))
    fwd = Vector((0, math.cos(L.SEATBACK_RECLINE), math.sin(L.SEATBACK_RECLINE)))
    return hinge, up, fwd


def _back_ring(s, variant, side_x, n_front=17):
    """Closed ring around the backrest at fraction s: front surface (sampled), outer flank, plastic back."""
    hinge, up, fwd = _back_frame()
    hw = back_half_w(s, variant)
    pts = []
    for i in range(n_front):
        x = -hw + 2 * hw * i / (n_front - 1)
        d = back_front(s, x, variant)
        # the outline edge rolls back a little so the pad reads wrapped
        edge = _sm(hw - 0.03, hw, abs(x))
        pts.append((x, d - 0.03 * edge))
    back = -0.045 + 0.012 * s
    pts += [(hw + 0.004, back + 0.03), (hw - 0.02, back), (0.0, back - 0.012), (-hw + 0.02, back), (-hw - 0.004, back + 0.03)]
    o = hinge + up * (s * BACK_H)
    return [o + Vector((side_x + x, 0, 0)) + fwd * d for x, d in pts]


# ---------------------------------------------------------------------------
# cushion surface
# ---------------------------------------------------------------------------
def cush_half_w(t):
    return L.SEAT_W / 2 - 0.02 * _sm(0.75, 1.0, t)


def cush_top(t):
    return L.CUSHION_TOP_Z - 0.015 * (1 - t) + 0.035 * _sm(0.55, 1.0, t) - 0.02 * _sm(0.93, 1.0, t)


def cush_bolster(t, x, hw, variant):
    amp = {'gt': 0.085, 'competition': 0.11, 'racing_shell': 0.12}[variant]
    env = 0.45 + 0.55 * math.sin(math.pi * min(1.0, max(0.0, (t + 0.05) / 1.05)))
    peak = hw - 0.062
    u = (abs(x) - peak) / 0.08
    shape = max(0.0, 1.0 - u * u)
    inner = _sm(hw - 0.18, hw - 0.11, abs(x))
    dish = -0.012 * max(0.0, 1.0 - (abs(x) / max(0.05, hw - 0.11)) ** 2) * (1.0 - _sm(0.75, 1.0, t))
    return amp * env * shape * inner + dish


def cush_surface(t, x, variant):
    hw = cush_half_w(t)
    return cush_top(t) + cush_bolster(t, x, hw, variant)


def _cushion_ring(y, variant, side_x, n_top=17):
    t = (y - L.CUSHION_Y0) / (L.CUSHION_Y1 - L.CUSHION_Y0)
    hw = cush_half_w(t)
    pts = []
    for i in range(n_top):
        x = -hw + 2 * hw * i / (n_top - 1)
        z = cush_surface(t, x, variant)
        edge = _sm(hw - 0.03, hw, abs(x))
        pts.append((x, z - 0.025 * edge))
    bottom = cush_top(t) - 0.12 - 0.03 * (1 - t)
    pts += [(hw + 0.004, bottom + 0.05), (hw - 0.02, bottom), (0.0, bottom - 0.008), (-hw + 0.02, bottom), (-hw - 0.004, bottom + 0.05)]
    return [Vector((side_x + x, y, z)) for x, z in pts]


def _smooth_ring(ring, n_per_seg=3):
    return lib.spline_through(ring, n_per_seg=n_per_seg, closed=True, tension=0.5)


def _panel(name, cid, rows, lift_vec, thickness=0.009, material='leather_black_perf', uv_scale=3.0, subsurf=1):
    """A sewn panel lying on a surface: rows of points (already lifted) lofted open, solidified inward."""
    obj = lib.loft_object(name, rows, close_u=False, material=material, uv_scale=uv_scale)
    lib.add_solidify(obj, thickness, offset=-1.0)
    if subsurf:
        lib.add_subsurf(obj, subsurf)
    lib.tag(obj, cid, 'seats')
    return obj


def build_seat(prefix, side_x, variant='gt'):
    hinge, up, fwd = _back_frame()
    # ------------------------------------------------------------------ cushion
    ys = [L.CUSHION_Y0, L.CUSHION_Y0 + 0.03, -0.17, -0.08, 0.0, 0.08, 0.16, L.CUSHION_Y1 - 0.06, L.CUSHION_Y1 - 0.02, L.CUSHION_Y1]
    rings = [_smooth_ring(_cushion_ring(y, variant, side_x)) for y in ys]
    base = lib.loft_object(f'{prefix}.base', rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=2.0)
    lib.add_subsurf(base, 1)
    lib.tag(base, f'{prefix}.base.bolsters', 'seats')
    # cushion insert: wide perforated panel with a rounded front, raised 7 mm
    rows = []
    for k in range(22):
        t = 0.06 + 0.86 * k / 21
        y = L.CUSHION_Y0 + (L.CUSHION_Y1 - L.CUSHION_Y0) * t
        w = 0.145 - 0.02 * _sm(0.8, 1.0, t) - 0.015 * (1 - _sm(0.0, 0.15, t))
        rows.append([Vector((side_x + x, y, cush_surface(t, x, variant) + 0.004)) for x in [-w + 2 * w * i / 10 for i in range(11)]])
    _panel(f'{prefix}.base.insert', f'{prefix}.base.center', rows, None)
    # ------------------------------------------------------------------ backrest (one piece, headrest integrated)
    ss = [0.0, 0.04, 0.10, 0.18, 0.27, 0.36, 0.45, 0.53, 0.60, 0.66, 0.72, 0.78, 0.84, 0.90, 0.95, 0.985, 1.0]
    rings = [_smooth_ring(_back_ring(s, variant, side_x)) for s in ss]
    back = lib.loft_object(f'{prefix}.back', rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=2.0)
    lib.add_subsurf(back, 1)
    lib.tag(back, f'{prefix}.back.bolsters', 'seats')
    # pass-through slot under the headrest pad (GT / competition), with a dark liner behind it
    if variant != 'racing_shell':
        surf = back_center_depth(SLOT_S, variant)
        so = hinge + up * (SLOT_S * BACK_H) + Vector((side_x, 0, 0)) + fwd * (surf + 0.10)
        cutter = lib.extrude_profile(f'{prefix}.slot_cut', lib.rounded_rect2d(0.165, 0.045, 0.012), so, Vector((1, 0, 0)), up, 0.32)  # (1,0,0) x up = -fwd: positive depth runs backward through the seat
        lib.add_boolean(back, cutter)
        # dark liner tube sits just inside the cut (its front edge 4 mm behind the pad surface)
        lo = hinge + up * (SLOT_S * BACK_H) + Vector((side_x, 0, 0)) + fwd * (surf - 0.004)
        liner = lib.extrude_profile(f'{prefix}.slot_liner', lib.rounded_rect2d(0.160, 0.040, 0.010), lo, Vector((1, 0, 0)), up, 0.12, material='plastic_black')
        lib.tag(liner, f'{prefix}.slot_liner', 'seats', selectable=False)
    # back centre insert: wide perforated panel from the lumbar to just under the slot
    rows = []
    for k in range(26):
        s = 0.07 + (SLOT_S - 0.045 - 0.07) * k / 25
        hw = back_half_w(s, variant)
        w = min(0.135, hw - 0.115) + 0.01 * _gauss(s, 0.5, 0.2)
        w -= 0.012 * (1 - _sm(0.07, 0.16, s))
        o = hinge + up * (s * BACK_H)
        rows.append([o + Vector((side_x + x, 0, 0)) + fwd * (back_front(s, x, variant) + 0.005) for x in [-w + 2 * w * i / 10 for i in range(11)]])
    _panel(f'{prefix}.back.insert', f'{prefix}.back.center', rows, None)
    # headrest pad: stitched rounded-top panel on the hooded top, carries the flags badge
    if variant != 'racing_shell':
        rows = []
        for k in range(14):
            s = PAD_S0 + (PAD_S1 - PAD_S0) * k / 13
            u = k / 13
            w = 0.105 * math.sqrt(max(0.0, 1.0 - (max(0.0, u - 0.55) / 0.45) ** 2))
            w = max(w, 0.02)
            o = hinge + up * (s * BACK_H)
            rows.append([o + Vector((side_x + x, 0, 0)) + fwd * (back_front(s, x, variant) + 0.010) for x in [-w + 2 * w * i / 10 for i in range(11)]])
        _panel(f'{prefix}.headrest', f'{prefix}.headrest', rows, None, thickness=0.012, material='leather_black', uv_scale=3.0)
    # harness slots for competition / racing
    if variant != 'gt':
        for sx in (-0.07, 0.07):
            s = 0.80
            slot_o = hinge + up * (s * BACK_H) + fwd * (back_center_depth(s, variant) + 0.03) + Vector((side_x + sx, 0, 0))
            slot = lib.extrude_profile(f'{prefix}.slot_{sx}', lib.rounded_rect2d(0.06, 0.02, 0.008), slot_o, Vector((1, 0, 0)), up, 0.06, material='plastic_black')
            lib.tag(slot, f'{prefix}.harness_slot.{"l" if sx < 0 else "r"}', 'seats', selectable=False)
    # ------------------------------------------------------------------ plastic back shell
    shell_rings = []
    for s in (0.02, 0.15, 0.3, 0.45, 0.6, 0.72, 0.84, 0.95):
        ring = _back_ring(s, variant, side_x)
        rear = ring[-5:]
        shell_rings.append([p - fwd * 0.012 for p in rear])
    shell = lib.loft_object(f'{prefix}.shell', shell_rings, close_u=False, material='plastic_black' if variant != 'racing_shell' else 'carbon', uv_scale=2.0)
    lib.add_solidify(shell, 0.012, offset=0.0)
    lib.add_subsurf(shell, 1)
    lib.tag(shell, f'{prefix}.back.shell', 'seats')
    # ------------------------------------------------------------------ frame, rails, outboard trim with switches, belt
    frame = lib.box(f'{prefix}.frame', (L.SEAT_W - 0.08, L.CUSHION_Y1 - L.CUSHION_Y0 - 0.04, 0.08), (side_x, 0.0, 0.12), material='plastic_black', bevel=0.01)
    lib.tag(frame, f'{prefix}.frame', 'seats', selectable=False)
    for tx in (-0.17, 0.17):
        rail = lib.box(f'{prefix}.rail_{tx}', (0.035, 0.56, 0.06), (side_x + tx, 0.0, 0.05), material='metal_satin_dark', bevel=0.004)
        lib.tag(rail, f'{prefix}.rail.{"l" if tx < 0 else "r"}', 'seats', selectable=False)
    out = 1 if side_x > 0 else -1
    trim = lib.box(f'{prefix}.side_trim', (0.035, 0.42, 0.10), (side_x + out * (L.SEAT_W / 2 - 0.01), -0.02, 0.19), material='plastic_black', bevel=0.012)
    lib.tag(trim, f'{prefix}.side_trim', 'seats', selectable=False)
    for k, (sy, sz) in enumerate(((0.08, 0.215), (0.0, 0.215), (-0.06, 0.215))):
        sw = lib.box(f'{prefix}.switch_{k}', (0.012, 0.05 if k == 0 else 0.035, 0.016), (side_x + out * (L.SEAT_W / 2 + 0.013), sy, sz), material='plastic_black_gloss', bevel=0.003)
        lib.tag(sw, f'{prefix}.seat_switch.{k}', 'seats', selectable=False)
    buckle = lib.box(f'{prefix}.buckle', (0.025, 0.05, 0.07), (side_x - out * (L.SEAT_W / 2 - 0.03), -0.17, 0.33), material='plastic_black_gloss', bevel=0.004)
    lib.tag(buckle, f'{prefix}.buckle', 'seats', selectable=False)
    p0 = Vector((side_x + out * 0.28, L.HALO_Y + 0.02, 0.88))
    p1 = Vector((side_x - out * 0.22, -0.15, 0.36))
    d = (p1 - p0).normalized()
    w = Vector((0, 0, 1)).cross(d).normalized() * 0.023
    strap_rings = [[c - w, c + w] for c in (p0, p0.lerp(p1, 0.5), p1)]
    strap = lib.loft_object(f'{prefix}.belt', strap_rings, close_u=False, material='seatbelt', uv_scale=4.0)
    lib.add_solidify(strap, 0.0015, offset=0.0)
    lib.tag(strap, f'{prefix}.seatbelt', 'seats')


def build(variant='gt', which=('driver', 'passenger')):
    if 'driver' in which:
        build_seat('seats.driver', -L.SEAT_X, variant)
    if 'passenger' in which:
        build_seat('seats.passenger', L.SEAT_X, variant)
