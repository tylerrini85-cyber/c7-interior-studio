"""Door panels (driver, passenger mirrored): upper pad, armrest with pull handle, release handle, window/lock switch
panel, speaker, map pocket, trim band, courtesy lamp, sill plate."""
import math
from mathutils import Vector
import lib
import layout as L


def _panel_section(y, side):
    """Open polyline (bottom -> top) of the inner door surface at station y, in X-Z; side = -1 driver, +1 passenger.
    Shape: lower moulded panel, padded armrest shelf, concave upper pad, thick rolled top bolster at the sill."""
    x_hip = L.CABIN_HALF_W_HIP
    x_sh = L.CABIN_HALF_W_SHOULDER
    s = (y - L.DOOR_Y_REAR) / (L.DOOR_Y_FRONT - L.DOOR_Y_REAR)
    arm_z = L.ARMREST_DOOR_Z
    bulge = math.sin(math.pi * min(1.0, max(0.0, (s - 0.10) / 0.80)))
    arm_in = L.ARMREST_DOOR_PROTRUSION * (0.30 + 0.70 * bulge)
    # the top bolster rises toward the front so the door meets the dash top at the A-pillar (sail area)
    t_rise = max(0.0, min(1.0, (s - 0.80) / 0.20))
    rise = 0.045 * t_rise * t_rise * (3 - 2 * t_rise)
    pts = [
        (x_hip + 0.03, L.ROCKER_TOP_Z + 0.02),
        (x_hip + 0.028, 0.30),
        (x_hip + 0.022, 0.42),
        (x_hip + 0.012, arm_z - 0.10),
        (x_hip - arm_in * 0.55, arm_z - 0.075),      # underside of the armrest shelf
        (x_hip - arm_in, arm_z - 0.035),
        (x_hip - arm_in - 0.004, arm_z + 0.0),        # rounded front edge
        (x_hip - arm_in * 0.55, arm_z + 0.018),       # flat padded top
        (x_hip - 0.012, arm_z + 0.022),
        (x_hip - 0.006, arm_z + 0.06),                # upper pad, slightly concave
        (x_hip - 0.0, 0.72 + rise),
        (x_sh - 0.03, 0.765 + rise),                  # rolled top bolster
        (x_sh - 0.045, L.SILL_Z - 0.02 + rise),
        (x_sh - 0.02, L.SILL_Z + 0.004 + rise),
        (x_sh + 0.03, L.SILL_Z + 0.004),
    ]
    return [Vector((side * x, y, z)) for x, z in pts]


def build_door(side):
    name = 'driver' if side < 0 else 'passenger'
    prefix = f'doors.{name}'
    ys = [L.DOOR_Y_REAR, -0.45, -0.3, -0.15, 0.0, 0.15, 0.3, 0.45, 0.58, L.DOOR_Y_FRONT]
    rings = [_panel_section(y, side) for y in ys]
    panel = lib.loft_object(f'{prefix}.panel', rings, close_u=False, material='leather_black', uv_scale=1.5, flip=side < 0)
    lib.add_subsurf(panel, 1)
    lib.tag(panel, f'{prefix}.panel', 'doors')
    # upper pad (leather) as a separate overlay strip above the trim band (for independent customisation)
    up_rings = []
    for y in ys:
        r = _panel_section(y, side)
        up_rings.append([p - Vector((side * 0.004, 0, 0)) for p in r[9:15]])
    upper = lib.loft_object(f'{prefix}.upper', up_rings, close_u=False, material='leather_black', uv_scale=1.5, flip=side < 0)
    lib.add_subsurf(upper, 1)
    lib.tag(upper, f'{prefix}.upper', 'doors')
    # lower panel overlay (carpet/plastic) below the armrest
    lo_rings = []
    for y in ys:
        r = _panel_section(y, side)
        lo_rings.append([p - Vector((side * 0.004, 0, 0)) for p in r[0:5]])
    lower = lib.loft_object(f'{prefix}.lower', lo_rings, close_u=False, material='plastic_black', uv_scale=1.5, flip=side < 0)
    lib.tag(lower, f'{prefix}.lower', 'doors')
    # armrest top pad (separate object): follows the bulge between y=-0.30 and y=0.45
    arm_rings = []
    for y in (-0.30, -0.15, 0.0, 0.15, 0.30, 0.45):
        r = _panel_section(y, side)
        arm_rings.append([p + Vector((0, 0, 0.004)) for p in r[4:10]])
    arm = lib.loft_object(f'{prefix}.armrest', arm_rings, close_u=False, material='leather_black', uv_scale=2.0, flip=side < 0)
    lib.add_subsurf(arm, 1)
    lib.tag(arm, f'{prefix}.armrest', 'doors')
    # ---- satin fin handle (IMG_4509 / IMG_4499 / IMG_4516): rises from the front of the armrest up and forward to a
    # wide head under the tweeter; the door release sits in the opening of the head; a dark hand pocket behind it
    # |x| of the visible (subdivided) door surface at (y, z): ray-cast against the evaluated panel and upper pad
    import bpy
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, dg) for o in (panel, upper)]

    def surf_x(y, z):
        best = None
        for t in trees:
            hit = t.ray_cast(Vector((side * 0.30, y, z)), Vector((side, 0, 0)), 1.0)
            if hit[0] is not None and (best is None or abs(hit[0].x) < best):
                best = abs(hit[0].x)
        if best is None:
            sec = _panel_section(y, 1)
            best = min(sec, key=lambda p: abs(p.z - z)).x
        return best
    fin_out = [(0.360, 0.598), (0.418, 0.598), (0.470, 0.640), (0.530, 0.690), (0.574, 0.716), (0.586, 0.740), (0.568, 0.756), (0.520, 0.756), (0.482, 0.738), (0.448, 0.700), (0.400, 0.640)]
    fin_out = [Vector(p) for p in lib.spline_through([Vector(p) for p in fin_out], n_per_seg=4, closed=True, tension=0.5)]
    hole = [Vector(p) for p in lib.spline_through([Vector(p) for p in ((0.506, 0.722), (0.552, 0.730), (0.562, 0.744), (0.522, 0.746))], n_per_seg=4, closed=True, tension=0.5)]
    x0 = min(surf_x(0.40, 0.62), surf_x(0.47, 0.68), surf_x(0.55, 0.73)) - 0.002
    fin = lib.extrude_profile(f'{prefix}.handle', fin_out, (side * x0, 0, 0), (0, 1, 0), (0, 0, 1), -side * 0.016, material='metal_brushed', bevel=0.003)
    cut = lib.extrude_profile(f'{prefix}.handle_hole', hole, (side * (x0 + 0.02), 0, 0), (0, 1, 0), (0, 0, 1), -side * 0.06)
    lib.add_boolean(fin, cut)
    lib.tag(fin, f'{prefix}.handle', 'doors')
    # release lever inside the head opening
    rel = lib.extrude_profile(f'{prefix}.release', [Vector(p) for p in ((0.514, 0.727), (0.548, 0.733), (0.552, 0.741), (0.520, 0.741))], (side * (x0 - 0.002), 0, 0), (0, 1, 0), (0, 0, 1), -side * 0.010, material='plastic_black_gloss', bevel=0.001)
    lib.tag(rel, f'{prefix}.release', 'doors', selectable=False)
    # dark hand pocket behind the fin (slightly larger than the fin, sunk into the panel)
    pocket_out = [Vector((p.x + (p.x - 0.47) * 0.08, p.y + (p.y - 0.68) * 0.10)) for p in fin_out]
    pk = lib.extrude_profile(f'{prefix}.pull_recess', pocket_out, (side * (x0 + 0.003), 0, 0), (0, 1, 0), (0, 0, 1), -side * 0.002, material='plastic_black')
    lib.tag(pk, f'{prefix}.pull_recess', 'doors', selectable=False)
    # window / lock switch pod on the armrest just behind the fin root
    s30 = (0.30 - L.DOOR_Y_REAR) / (L.DOOR_Y_FRONT - L.DOOR_Y_REAR)
    arm_in30 = L.ARMREST_DOOR_PROTRUSION * (0.30 + 0.70 * math.sin(math.pi * min(1.0, max(0.0, (s30 - 0.10) / 0.80))))
    xs = side * (L.CABIN_HALF_W_HIP - arm_in30 * 0.55 + 0.004)
    sw = lib.extrude_profile(f'{prefix}.switches', lib.rounded_rect2d(0.044, 0.085, 0.010), (xs, 0.29, L.ARMREST_DOOR_Z + 0.020), (1, 0, 0), (0, 1, 0), 0.004, material='plastic_black_gloss', bevel=0.002)
    lib.tag(sw, f'{prefix}.switches', 'doors', selectable=False)
    for k in range(2):
        b = lib.box(f'{prefix}.winsw_{k}', (0.020, 0.026, 0.009), (xs, 0.31 - 0.034 * k, L.ARMREST_DOOR_Z + 0.027), material='plastic_black', bevel=0.003)
        lib.tag(b, f'{prefix}.winsw.{k}', 'doors', selectable=False)
    # speaker grille (round) low in the front of the door
    sy, sz = L.SPEAKER_CENTER
    spk = lib.revolve(f'{prefix}.speaker', [(0.0, 0.0), (0.085, 0.0), (0.09, 0.006), (0.0, 0.006)], segments=40, material='plastic_black', origin=(side * (L.CABIN_HALF_W_HIP + 0.02), sy, sz), direction=(-side, 0, 0))
    lib.tag(spk, f'{prefix}.speaker', 'doors')
    ring = lib.revolve(f'{prefix}.speaker_ring', [(0.085, 0.0), (0.095, 0.0), (0.095, 0.008), (0.085, 0.008)], segments=40, material='metal_brushed', origin=(side * (L.CABIN_HALF_W_HIP + 0.02), sy, sz), direction=(-side, 0, 0))
    lib.tag(ring, f'{prefix}.speaker_ring', 'trim', selectable=False)
    # tweeter sail near the mirror: triangular grille on the upper front of the door (IMG_4509)
    tri = [Vector(p) for p in lib.spline_through([Vector(p) for p in ((0.600, 0.792), (0.700, 0.808), (0.760, 0.806), (0.758, 0.720), (0.700, 0.742))], n_per_seg=3, closed=True, tension=0.4)]
    sail = lib.extrude_profile(f'{prefix}.sail', tri, (side * (surf_x(0.70, 0.77) + 0.004), 0, 0), (0, 1, 0), (0, 0, 1), -side * 0.010, material='plastic_black', bevel=0.003)
    rim = lib.sweep_tube(f'{prefix}.sail_rim', [Vector((side * (surf_x(0.70, 0.77) - 0.006), p.x, p.y)) for p in tri] + [Vector((side * (surf_x(0.70, 0.77) - 0.006), tri[0].x, tri[0].y))], 0.0018, n=8, cap=True, material='metal_brushed', up_hint=Vector((side, 0, 0)))
    lib.tag(rim, f'{prefix}.sail_rim', 'trim', selectable=False)
    lib.tag(sail, f'{prefix}.sail', 'doors', selectable=False)
    # map pocket: open bin along the lower door
    pocket = lib.box(f'{prefix}.pocket', (0.05, 0.45, 0.10), (side * (L.CABIN_HALF_W_HIP - 0.0), -0.12, 0.30), material='plastic_black', bevel=0.008)
    lib.tag(pocket, f'{prefix}.pocket', 'doors')
    # diagonal accent line (IMG_4516 / IMG_4509): from below the tweeter, down and rearward across the upper pad
    pts, nrms = [], []
    for i in range(16):
        t = i / 15
        y = 0.62 + (-0.42 - 0.62) * t
        z = 0.765 + (0.640 - 0.765) * t
        pts.append(Vector((side * (surf_x(y, z) - 0.0015), y, z))); nrms.append(Vector((-side, 0, 0)))
    band = lib.ribbon(f'{prefix}.trim', pts, nrms, 0.010, 0.004, material='metal_brushed', uv_scale=2.0)
    lib.tag(band, f'{prefix}.trim', 'trim')
    # courtesy lamp near the bottom rear and the sill plate
    lamp = lib.box(f'{prefix}.lamp', (0.01, 0.04, 0.012), (side * (L.CABIN_HALF_W_HIP + 0.02), -0.40, 0.22), material='emissive_white')
    lib.tag(lamp, f'lighting.door.{name}', 'lighting', selectable=False)
    sill = lib.box(f'{prefix}.sill_plate', (0.09, 0.9, 0.004), (side * (L.ROCKER_HALF_W - 0.06), 0.08, L.ROCKER_TOP_Z + 0.002), material='metal_brushed', bevel=0.001)
    lib.tag(sill, f'{prefix}.sill_plate', 'trim', selectable=False)


def build():
    build_door(-1)
    build_door(1)
