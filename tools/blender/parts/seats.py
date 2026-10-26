"""Seats. Factory GT seat (baseline) with centre inserts, bolsters, integrated headrest, plastic back shell, base trim,
seatbelt buckle. Variants: competition (deeper bolsters, harness slots), racing_shell (fixed-back carbon bucket)."""
import math
from mathutils import Vector
import lib
import layout as L

VARIANTS = ['gt', 'competition', 'racing_shell']


def _cushion_ring(y, variant, side_x):
    """Closed ring (X-Z around the cushion) at station y, local X relative to seat centre."""
    hw = L.SEAT_W / 2
    s = (y - L.CUSHION_Y0) / (L.CUSHION_Y1 - L.CUSHION_Y0)   # 0 rear -> 1 front
    top = L.CUSHION_TOP_Z + 0.03 * (s ** 2) - 0.01 * (1 - s)   # front thigh lip rises
    bol = 0.075 if variant == 'gt' else 0.105
    bol *= (0.55 + 0.45 * math.sin(math.pi * min(1.0, s * 1.15)))  # bolsters taper at the very front and rear
    if variant == 'racing_shell':
        bol = 0.12 * (0.6 + 0.4 * math.sin(math.pi * s))
    bottom = top - 0.11 - 0.03 * (1 - s)
    pts = [
        (-hw, bottom + 0.02), (-hw + 0.005, top - 0.01), (-hw + 0.03, top + bol * 0.85), (-hw + 0.07, top + bol), (-hw + 0.12, top + bol * 0.55),
        (-hw + 0.16, top + 0.012), (-0.06, top), (0.0, top - 0.003), (0.06, top),
        (hw - 0.16, top + 0.012), (hw - 0.12, top + bol * 0.55), (hw - 0.07, top + bol), (hw - 0.03, top + bol * 0.85), (hw - 0.005, top - 0.01), (hw, bottom + 0.02),
        (hw - 0.03, bottom), (0.0, bottom - 0.005), (-hw + 0.03, bottom),
    ]
    return [Vector((side_x + x, y, z)) for x, z in pts]


def _back_frame():
    """Returns (origin at the hinge, up axis along the seatback, forward axis)."""
    hinge = Vector((0.0, L.CUSHION_Y0 + 0.02, L.CUSHION_TOP_Z - 0.02))
    up = Vector((0, -math.sin(L.SEATBACK_RECLINE), math.cos(L.SEATBACK_RECLINE)))
    fwd = Vector((0, math.cos(L.SEATBACK_RECLINE), math.sin(L.SEATBACK_RECLINE)))
    return hinge, up, fwd


def _back_ring(h, variant, side_x):
    """Closed ring around the seatback at height h (0..SEATBACK_H) along the recline axis: X across, depth along fwd."""
    hinge, up, fwd = _back_frame()
    s = h / L.SEATBACK_H
    # GT backrest: constant width low, flares at the shoulder wings (~75%), then narrows to the neck
    wing = max(0.0, 1.0 - abs(s - 0.76) / 0.16)
    wing = wing * wing * (3 - 2 * wing)
    top = max(0.0, min(1.0, (s - 0.80) / 0.20)); top = top * top * (3 - 2 * top)
    hw = L.SEAT_W / 2 - 0.005 + 0.018 * wing - 0.06 * top
    # lumbar S-curve: surface pushes forward at 25-40% height, recedes at the shoulders
    lumbar = 0.035 * math.exp(-((s - 0.32) / 0.2) ** 2) - 0.01 * s
    bol = (0.055 + 0.05 * math.sin(math.pi * min(1.0, s * 1.05))) if variant == 'gt' else (0.075 + 0.08 * math.sin(math.pi * min(1.0, s * 1.05)))
    if variant == 'racing_shell':
        bol = 0.09 + 0.09 * math.sin(math.pi * s)
    if s > 0.72:  # shoulder wings extend further forward
        bol += 0.045 * ((s - 0.72) / 0.28) if variant != 'racing_shell' else 0.0
    front = 0.065 + lumbar
    back = -0.042 + 0.012 * s
    pts2 = [
        (-hw, back + 0.02), (-hw + 0.005, front - 0.015), (-hw + 0.03, front + bol * 0.85), (-hw + 0.07, front + bol), (-hw + 0.12, front + bol * 0.5),
        (-hw + 0.16, front + 0.01), (-0.06, front), (0.0, front - 0.003), (0.06, front),
        (hw - 0.16, front + 0.01), (hw - 0.12, front + bol * 0.5), (hw - 0.07, front + bol), (hw - 0.03, front + bol * 0.85), (hw - 0.005, front - 0.015), (hw, back + 0.02),
        (hw - 0.04, back), (0.0, back - 0.01), (-hw + 0.04, back),
    ]
    o = hinge + up * h
    return [o + Vector((side_x + x, 0, 0)) + fwd * d for x, d in pts2]


def _smooth_ring(ring, n_per_seg=3):
    return lib.spline_through(ring, n_per_seg=n_per_seg, closed=True, tension=0.5)


def _insert_strip(name, rings_fn, stations, half_w, lift, material, cid, uv_scale=3.0, pleats=0):
    """Centre insert panel: the centre portion of the surface raised by `lift`, with optional pleat ribs
    (the C7 GT insert has horizontal pleats sewn across it)."""
    n = len(stations)
    rings = []
    for i, st in enumerate(stations):
        ring = rings_fn(st)
        sub = [Vector(p) for p in ring[5:10]]
        t = i / max(1, n - 1)
        rib = 1.0
        if pleats:
            rib = 1.0 + 0.9 * max(0.0, math.sin(math.pi * pleats * t)) ** 1.5
        rings.append([p + lift * rib for p in sub])
    obj = lib.loft_object(name, rings, close_u=False, material=material, uv_scale=uv_scale)
    lib.add_solidify(obj, 0.012, offset=-1.0)
    lib.add_subsurf(obj, 1)
    lib.tag(obj, cid, 'seats')
    return obj


def build_seat(prefix, side_x, variant='gt'):
    # ---- base cushion (bolsters + body)
    ys = [L.CUSHION_Y0, L.CUSHION_Y0 + 0.04, -0.15, -0.05, 0.05, 0.15, L.CUSHION_Y1 - 0.05, L.CUSHION_Y1 - 0.015, L.CUSHION_Y1]
    rings = [_smooth_ring(_cushion_ring(y, variant, side_x)) for y in ys]
    base = lib.loft_object(f'{prefix}.base', rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=2.0)
    lib.add_subsurf(base, 1)
    lib.tag(base, f'{prefix}.base.bolsters', 'seats')
    base_st = [L.CUSHION_Y0 + 0.04 + (L.CUSHION_Y1 - 0.05 - L.CUSHION_Y0 - 0.04) * i / 23 for i in range(24)]
    _insert_strip(f'{prefix}.base.insert', lambda y: _cushion_ring(y, variant, side_x), base_st, 0.16, Vector((0, 0, 0.007)), 'leather_black_perf', f'{prefix}.base.center', pleats=0 if variant == 'racing_shell' else 3)
    # ---- seatback
    hs = [0.0, 0.05, 0.12, 0.2, 0.3, 0.4, 0.5, 0.58, L.SEATBACK_H - 0.03, L.SEATBACK_H]
    rings = [_smooth_ring(_back_ring(h, variant, side_x)) for h in hs]
    back = lib.loft_object(f'{prefix}.back', rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=2.0)
    lib.add_subsurf(back, 1)
    lib.tag(back, f'{prefix}.back.bolsters', 'seats')
    hinge, up, fwd = _back_frame()
    back_st = [0.05 + (L.SEATBACK_H - 0.08) * i / 35 for i in range(36)]
    _insert_strip(f'{prefix}.back.insert', lambda h: _back_ring(h, variant, side_x), back_st, 0.16, fwd * 0.007, 'leather_black_perf', f'{prefix}.back.center', pleats=0 if variant == 'racing_shell' else 6)
    # ---- headrest (integrated): neck + head pad
    if variant != 'racing_shell':
        top_o = hinge + up * L.SEATBACK_H + Vector((side_x, 0, 0))
        neck_rings = []
        for s, (w, d, h) in ((0.0, (0.22, 0.10, -0.01)), (0.4, (0.17, 0.085, 0.03)), (1.0, (0.16, 0.08, 0.06))):
            prof = lib.rounded_rect2d(w, d, 0.03)
            neck_rings.append(lib.place_profile(prof, top_o + up * h + fwd * 0.02, Vector((1, 0, 0)), fwd))
        neck = lib.loft_object(f'{prefix}.neck', neck_rings, close_u=True, cap_start=True, cap_end=False, material='leather_black', uv_scale=3.0)
        lib.add_subsurf(neck, 1)
        lib.tag(neck, f'{prefix}.headrest.neck', 'seats', selectable=False)
        head_rings = []
        for s, (w, d, h) in ((0.0, (0.21, 0.08, 0.055)), (0.25, (0.255, 0.105, 0.085)), (0.75, (0.255, 0.105, 0.155)), (1.0, (0.22, 0.085, 0.185))):
            prof = lib.rounded_rect2d(w, d, 0.04, n_corner=8)
            head_rings.append(lib.place_profile(prof, top_o + up * h + fwd * (0.03 + 0.12 * h), Vector((1, 0, 0)), fwd))
        head = lib.loft_object(f'{prefix}.headrest', head_rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=3.0)
        lib.add_subsurf(head, 1)
        lib.tag(head, f'{prefix}.headrest', 'seats')
        # embroidery placeholder patch on the headrest front (text 'C7')
        hc = top_o + up * 0.125 + fwd * (0.03 + 0.115 / 2 + 0.002)
        txt = lib.text_object(f'{prefix}.headrest.text', 'C7', 0.028, hc, Vector((1, 0, 0)), up, extrude=0.0004, material='stitch_grey')
        lib.tag(txt, f'{prefix}.headrest.embroidery', 'seats', selectable=False)
    else:
        # racing shell: tall one-piece back with head surround and harness slots
        top_o = hinge + up * L.SEATBACK_H + Vector((side_x, 0, 0))
        rings = []
        for s, (w, d, h) in ((0.0, (0.46, 0.16, -0.02)), (0.5, (0.40, 0.17, 0.10)), (1.0, (0.30, 0.12, 0.22))):
            rings.append(lib.place_profile(lib.rounded_rect2d(w, d, 0.05), top_o + up * h - fwd * 0.02, Vector((1, 0, 0)), fwd))
        head = lib.loft_object(f'{prefix}.headrest', rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=3.0)
        lib.add_subsurf(head, 2)
        lib.tag(head, f'{prefix}.headrest', 'seats')
    # harness slots for competition / racing
    if variant != 'gt':
        for sx in (-0.07, 0.07):
            slot_o = hinge + up * (L.SEATBACK_H - 0.08) + fwd * 0.10 + Vector((side_x + sx, 0, 0))
            slot = lib.extrude_profile(f'{prefix}.slot_{sx}', lib.rounded_rect2d(0.06, 0.02, 0.008), slot_o, Vector((1, 0, 0)), up, -0.05, material='plastic_black')
            lib.tag(slot, f'{prefix}.harness_slot.{"l" if sx < 0 else "r"}', 'seats', selectable=False)
    # ---- plastic back shell (behind the seatback)
    shell_rings = []
    for h in (0.02, 0.2, 0.4, 0.58, L.SEATBACK_H - 0.02):
        ring = _back_ring(h, variant, side_x)
        rear = ring[14:18] + ring[0:1]
        shell_rings.append([p - fwd * 0.012 for p in rear])
    shell = lib.loft_object(f'{prefix}.shell', shell_rings, close_u=False, material='plastic_black' if variant != 'racing_shell' else 'carbon', uv_scale=2.0)
    lib.add_solidify(shell, 0.01, offset=0.0)
    lib.tag(shell, f'{prefix}.back.shell', 'seats')
    # ---- base frame / track trim
    frame = lib.box(f'{prefix}.frame', (L.SEAT_W - 0.06, L.CUSHION_Y1 - L.CUSHION_Y0 - 0.02, 0.09), (side_x, 0.0, 0.13), material='plastic_black', bevel=0.01)
    lib.tag(frame, f'{prefix}.frame', 'seats', selectable=False)
    for tx in (-0.17, 0.17):
        rail = lib.box(f'{prefix}.rail_{tx}', (0.035, 0.56, 0.06), (side_x + tx, 0.0, 0.05), material='metal_satin_dark', bevel=0.004)
        lib.tag(rail, f'{prefix}.rail.{"l" if tx < 0 else "r"}', 'seats', selectable=False)
    # outboard side trim with power seat switches
    out = 1 if side_x > 0 else -1
    trim = lib.box(f'{prefix}.side_trim', (0.03, 0.40, 0.09), (side_x + out * (L.SEAT_W / 2 - 0.005), -0.02, 0.20), material='plastic_black', bevel=0.008)
    lib.tag(trim, f'{prefix}.side_trim', 'seats', selectable=False)
    sw = lib.box(f'{prefix}.switch', (0.012, 0.09, 0.02), (side_x + out * (L.SEAT_W / 2 + 0.015), 0.02, 0.22), material='plastic_black_gloss', bevel=0.003)
    lib.tag(sw, f'{prefix}.seat_switch', 'seats', selectable=False)
    # seatbelt buckle on the inboard side and the belt strap over the shoulder from the halo
    buckle = lib.box(f'{prefix}.buckle', (0.025, 0.05, 0.07), (side_x - out * (L.SEAT_W / 2 - 0.02), -0.17, 0.33), material='plastic_black_gloss', bevel=0.004)
    lib.tag(buckle, f'{prefix}.buckle', 'seats', selectable=False)
    # belt webbing: from the halo (outboard shoulder) diagonally down to the buckle, modelled as a flat strap
    p0 = Vector((side_x + out * 0.28, L.HALO_Y + 0.02, 0.88))
    p1 = Vector((side_x - out * 0.22, -0.15, 0.36))
    strap_rings = []
    for s in (0.0, 0.5, 1.0):
        c = p0.lerp(p1, s)
        strap_rings.append([c + Vector((0, 0.0, 0)) + Vector((-0.023 * (1 - 0) * 0, 0, 0)), c])
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
