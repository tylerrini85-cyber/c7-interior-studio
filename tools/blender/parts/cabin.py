"""Cabin shell: floor, tunnel, toe board, rocker sills, A-pillars, windshield, roof/headliner, targa panel, halo bar,
rear bulkhead, cargo floor, rear glass, side glass, B-pillar trim, visors, mirror, overhead console, pedals."""
import math
from mathutils import Vector
import lib
import layout as L


def _floor_section(y, z_base=0.0):
    """Open polyline across X for the floor at a given Y including the tunnel hump."""
    hw = L.ROCKER_HALF_W - 0.005
    t = L.TUNNEL_HALF_W
    tz = L.TUNNEL_Z + z_base
    pts = [
        (-hw, y, z_base), (-hw + 0.05, y, z_base), (-t - 0.10, y, z_base), (-t - 0.03, y, z_base + 0.03),
        (-t, y, tz - 0.06), (-t + 0.03, y, tz), (0.0, y, tz + 0.01), (t - 0.03, y, tz),
        (t, y, tz - 0.06), (t + 0.03, y, z_base + 0.03), (t + 0.10, y, z_base), (hw - 0.05, y, z_base), (hw, y, z_base),
    ]
    return [Vector(p) for p in pts]


def build_floor():
    rings = []
    for y in (L.REAR_BULKHEAD_Y, -0.45, -0.2, 0.05, 0.3, 0.55, L.TOEBOARD_Y0):
        rings.append(_floor_section(y))
    # toe board rising to the dash lower
    for k in range(1, 5):
        s = k / 4
        y = L.TOEBOARD_Y0 + (L.TOEBOARD_Y1 - L.TOEBOARD_Y0) * s
        z = L.TOEBOARD_Z1 * (s ** 1.4)
        rings.append(_floor_section(y, z_base=z))
    obj = lib.loft_object('floor.carpet', rings, close_u=False, material='carpet_black', uv_scale=2.0)
    lib.tag(obj, 'floor.carpet', 'floor')
    # floor mats (two)
    for side, cid in ((-1, 'floor.mats.driver'), (1, 'floor.mats.passenger')):
        x = side * (L.SEAT_X + 0.01)
        # shaped mat: wide at the heel, tapering toward the toe board, inboard edge following the tunnel
        pts = [(-0.20, -0.14), (0.20, -0.14), (0.21, 0.10), (0.17, 0.30), (0.08, 0.40), (-0.08, 0.40), (-0.17, 0.30), (-0.21, 0.10)]
        if side > 0:
            pts = [(-px, py) for (px, py) in pts]
        prof = lib.spline_through([Vector(p) for p in pts], n_per_seg=4, closed=True, tension=0.5)
        mat = lib.extrude_profile(cid, [Vector((p.x, p.y)) for p in prof], (x, 0.36, 0.006), (1, 0, 0), (0, 1, 0), 0.012, material='carpet_black', uv_scale=3.0)
        lib.add_bevel(mat, 0.004, 2)
        lib.tag(mat, cid, 'floor')
    return obj


def build_rockers():
    for side in (-1, 1):
        x0 = side * (L.ROCKER_HALF_W - L.ROCKER_W / 2)
        prof = lib.rounded_rect2d(L.ROCKER_W, L.ROCKER_TOP_Z, 0.03)
        o = lib.extrude_profile(f'rocker_{side}', prof, (x0, L.DOOR_Y_REAR - 0.12, L.ROCKER_TOP_Z / 2), (1, 0, 0), (0, 0, 1), L.DOOR_Y_FRONT - L.DOOR_Y_REAR + 0.3, material='plastic_black')
        lib.tag(o, 'sill.driver' if side < 0 else 'sill.passenger', 'trim', selectable=False)


def _roof_z(x, y):
    """Headliner underside height; curved in X, slight bow in Y."""
    xs = (x / L.ROOF_HALF_W) ** 2
    z = L.HEADLINER_Z - (L.HEADLINER_Z - L.HEADLINER_SIDE_Z) * xs
    # slope down toward header and halo slightly
    yf = (y - (L.HEADER_Y + L.HALO_Y) / 2) / ((L.HEADER_Y - L.HALO_Y) / 2)
    z -= 0.015 * yf * yf
    return z


def _down_faces(rings):
    """True when the default loft winding of rings (lines across x, stepping in y) faces up; used to flip to face down."""
    a, b, d = Vector(rings[0][0]), Vector(rings[0][1]), Vector(rings[1][0])
    return (b - a).cross(d - a).z > 0


def _roof_patch(cid, xs, ys, dz=0.0, material='headliner_suede', category='roof', selectable=True, edge=None):
    """A piece of the one headliner surface: lines across x at each y, z on _roof_z (+dz), facing down. edge(x, y)
    optionally overrides a point (used for the rolled outer edges)."""
    rings = []
    for y in ys:
        ring = []
        for x in xs:
            pt = Vector((x, y, _roof_z(x, y) + dz))
            if edge:
                pt = edge(pt)
            ring.append(pt)
        rings.append(ring)
    obj = lib.loft_object(cid, rings, close_u=False, material=material, uv_scale=2.0, flip=_down_faces(rings))
    lib.tag(obj, cid, category, selectable=selectable)
    return obj


def _lin(a, b, n):
    return [a + (b - a) * k / (n - 1) for k in range(n)]


ROOF_FRONT_Y = 0.395            # headliner front edge, tucked over by the windshield header trim
ROOF_REAR_Y = -0.53             # rear edge, under the halo trim
SEAM = 0.004                    # half width of the groove around the removable panel


def build_roof():
    """One continuous headliner: the fixed header, side rails and rear strip and the removable roof panel are all cut
    from the same curved surface, so they meet edge to edge; the panel sits 2 mm up behind a narrow dark groove (a
    backing strip behind the gap), as on the car. The side rails roll down at the outer edge to meet the glass."""
    W, T = L.ROOF_HALF_W, L.TARGA_HALF_W
    fy, ry = L.TARGA_Y_FRONT, L.TARGA_Y_REAR
    xs_full = _lin(-W, W, 25)
    _roof_patch('roof.header', xs_full, _lin(ROOF_FRONT_Y, fy + SEAM, 4))
    _roof_patch('roof.rear_strip', xs_full, _lin(ry - SEAM, ROOF_REAR_Y, 3))
    for side in (-1, 1):
        xs = _lin(side * (T + SEAM), side * W, 6) + [side * (W + 0.010)]
        def roll(pt, side=side):
            # outermost column: roll down 22 mm to meet the top of the side glass
            if abs(pt.x) > W + 0.005:
                pt.z -= 0.022
            return pt
        if side < 0:
            xs = list(reversed(xs))
        _roof_patch('roof.rail.driver' if side < 0 else 'roof.rail.passenger', xs, _lin(fy + SEAM, ry - SEAM, 10), edge=roll)
    _roof_patch('roof.panel', _lin(-(T - SEAM), T - SEAM, 21), _lin(fy - SEAM, ry + SEAM, 12), dz=0.002)
    # dark backing seen through the groove
    _roof_patch('roof.seam', _lin(-(T + 0.012), T + 0.012, 21), _lin(fy + 0.012, ry - 0.012, 12), dz=0.010, material='plastic_black', selectable=False)


def build_halo():
    """Halo (B-pillar hoop) trim: a broad flat band (110 mm along the car, 30 mm deep) arching from the beltline behind
    each door up the side and across under the roof at the rear of the removable panel."""
    W = L.CABIN_HALF_W_SHOULDER - 0.012
    y = L.HALO_Y
    ctrl = [Vector((-W, y, L.SILL_Z - 0.02)), Vector((-W, y, 0.93)), Vector((-W + 0.006, y, 0.975)), Vector((-W + 0.03, y, 1.005))]
    for x in _lin(-0.62, 0.62, 9):
        ctrl.append(Vector((x, y, _roof_z(x, y) - 0.002)))
    ctrl += [Vector((W - 0.03, y, 1.005)), Vector((W - 0.006, y, 0.975)), Vector((W, y, 0.93)), Vector((W, y, L.SILL_Z - 0.02))]
    path = lib.resample_open(lib.spline_through(ctrl, n_per_seg=6, tension=0.5), 90)
    prof = lib.rounded_rect2d(0.110, 0.030, 0.012, n_corner=4)
    rings = []
    for i, p in enumerate(path):
        t = (path[min(len(path) - 1, i + 1)] - path[max(0, i - 1)]).normalized()
        n = Vector((0, 1, 0)).cross(t).normalized()          # in the hoop plane, perpendicular to the path
        if n.dot(Vector((0, y, 0.55)) - p) < 0:             # point it into the cabin
            n = -n
        rings.append([p + Vector((0, q.x, 0)) + n * (q.y + 0.015) for q in prof])
    halo = lib.loft_object('pillar.halo', rings, close_u=True, cap_start=True, cap_end=True, material='suede_black', uv_scale=2.0)
    a, b, d = rings[5][0], rings[5][1], rings[6][0]
    if (b - a).cross(d - a).dot(Vector((0, y, 0.55)) - rings[5][0]) > 0:
        bpy_remove(halo)
        halo = lib.loft_object('pillar.halo', rings, close_u=True, cap_start=True, cap_end=True, material='suede_black', uv_scale=2.0, flip=True)
    lib.tag(halo, 'pillar.halo', 'pillars')


def bpy_remove(obj):
    import bpy
    me = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.meshes.remove(me)


def build_a_pillars_and_glass():
    for side in (-1, 1):
        # padded A-pillar trim: a broad, slightly domed shell (85 mm) from the windshield edge outward over the pillar,
        # running from the dash corner up into the header trim
        base = Vector((side * L.WINDSHIELD_HALF_W_BASE, L.COWL_Y, L.COWL_Z))
        top = Vector((side * L.WINDSHIELD_HALF_W_TOP, L.HEADER_Y, L.HEADER_Z))
        t = (top - base).normalized()
        out = Vector((side, 0, 0))
        ax = (out - t * out.dot(t)).normalized()
        bx = t.cross(ax).normalized()
        if bx.dot(Vector((-side, -0.6, -0.3))) < 0:
            bx = -bx
        prof = [(-0.012, 0.000), (0.000, 0.020), (0.022, 0.032), (0.050, 0.031), (0.072, 0.019), (0.086, 0.002), (0.070, -0.008), (0.000, -0.008)]
        rings = []
        for k in range(15):
            sk = k / 12                             # runs ~15 % past the glass corner, up into the header trim
            p = base + (top - base) * sk
            p.x += side * 0.02 * math.sin(math.pi * sk)
            w = 1.0 - 0.15 * sk                     # a little narrower at the top
            rings.append([p + ax * (q[0] * w) + bx * q[1] for q in prof])
        a_, b_, d_ = rings[3][1], rings[3][2], rings[4][1]
        flip = (b_ - a_).cross(d_ - a_).dot(bx) < 0
        pil = lib.loft_object(f'pillar.a_{side}', rings, close_u=True, cap_start=True, cap_end=True, material='suede_black', uv_scale=2.0, flip=flip)
        lib.tag(pil, 'pillar.a.driver' if side < 0 else 'pillar.a.passenger', 'pillars')
    # windshield glass: loft from base curve to top curve with slight cylindrical bow forward in the centre
    n = 15
    def curve(y, z, hw, bow):
        return [Vector((x, y + bow * (1 - (x / hw) ** 2), z)) for x in [(-hw + 2 * hw * i / (n - 1)) for i in range(n)]]
    rings = []
    for k in range(5):
        s = k / 4
        y = L.COWL_Y + (L.HEADER_Y - L.COWL_Y) * s
        z = L.COWL_Z + (L.HEADER_Z - L.COWL_Z) * s
        hw = L.WINDSHIELD_HALF_W_BASE + (L.WINDSHIELD_HALF_W_TOP - L.WINDSHIELD_HALF_W_BASE) * s
        rings.append(curve(y, z, hw, 0.06))
    ws = lib.loft_object('glass.windshield', rings, close_u=False, material='glass')
    lib.tag(ws, 'glass.windshield', 'glass', selectable=False)
    # windshield header trim: a padded strip bridging the glass's top edge and the headliner's front edge (no gap
    # between them anywhere along the bowed glass)
    rings = []
    hw = L.WINDSHIELD_HALF_W_TOP
    for x in _lin(-hw - 0.03, hw + 0.03, 25):
        xc = max(-hw, min(hw, x))
        g = Vector((x, L.HEADER_Y + 0.06 * (1 - (xc / hw) ** 2), L.HEADER_Z))
        h = Vector((x, ROOF_FRONT_Y - 0.01, _roof_z(x, ROOF_FRONT_Y - 0.01)))
        m = g.lerp(h, 0.5)
        lo = min(g.z, h.z)
        ring = [g + Vector((0, 0.012, 0.006)), g + Vector((0, 0.002, -0.012)), Vector((m.x, m.y, lo - 0.020)),
                h + Vector((0, 0.0, -0.010)), h + Vector((0, -0.010, 0.004)), Vector((m.x, m.y, max(g.z, h.z) + 0.012))]
        # beyond the glass corners the trim rounds off and turns down over the pillar tops
        over = max(0.0, abs(x) - hw) / 0.03
        if over > 0:
            cen = sum(ring, Vector((0, 0, 0))) / len(ring)
            k_ = 1.0 - 0.45 * over
            ring = [cen + (q - cen) * k_ + Vector((0, 0.010, -0.018)) * over for q in ring]
        rings.append(ring)
    a_, b_, d_ = rings[10][1], rings[10][2], rings[11][1]
    flip = (b_ - a_).cross(d_ - a_).z > 0
    hdr = lib.loft_object('pillar.header', rings, close_u=True, cap_start=True, cap_end=True, material='suede_black', uv_scale=2.0, flip=flip)
    lib.tag(hdr, 'pillar.header', 'pillars')
    # side (door) glass per side: from sill to roof rail, front edge along A-pillar slope, rear at B-pillar
    for side in (-1, 1):
        x_sill = side * (L.CABIN_HALF_W_SHOULDER + 0.01)
        x_top = side * (L.ROOF_HALF_W + 0.005)
        rings = []
        for k in range(4):
            s = k / 3
            z = L.SILL_Z + (L.HEADLINER_SIDE_Z - 0.02 - L.SILL_Z) * s
            x = x_sill + (x_top - x_sill) * s
            # front edge follows the A-pillar line (y depends on z)
            y_front = L.COWL_Y + (L.HEADER_Y - L.COWL_Y) * ((z - L.COWL_Z) / (L.HEADER_Z - L.COWL_Z))
            y_rear = L.HALO_Y + 0.05
            rings.append([Vector((x, y_rear + (y_front - y_rear) * i / 6, z)) for i in range(7)])
        g = lib.loft_object(f'glass.side_{side}', rings, close_u=False, material='glass')
        lib.tag(g, 'glass.side.driver' if side < 0 else 'glass.side.passenger', 'glass', selectable=False)


def build_rear():
    # bulkhead panel behind seats
    hw = L.CABIN_HALF_W_HIP
    prof = lib.rounded_rect2d(2 * hw, L.CARGO_FLOOR_Z, 0.02)
    bh = lib.extrude_profile('rear.bulkhead', prof, (0, L.REAR_BULKHEAD_Y, L.CARGO_FLOOR_Z / 2), (1, 0, 0), (0, 0, 1), -0.04, material='carpet_black', uv_scale=2.0)
    lib.tag(bh, 'rear.bulkhead', 'rear')
    # cargo floor
    y0 = L.REAR_BULKHEAD_Y
    y1 = L.REAR_GLASS_END[0] + 0.1
    rings = [[Vector((x, y, L.CARGO_FLOOR_Z)) for x in (-hw, -hw / 2, 0, hw / 2, hw)] for y in (y0, (y0 + y1) / 2, y1)]
    cf = lib.loft_object('rear.cargo_floor', rings, close_u=False, material='carpet_black', uv_scale=2.0, flip=True)
    lib.tag(cf, 'rear.cargo_floor', 'rear')
    # rear quarter trim panels (behind the doors, below the glass), both sides
    for side in (-1, 1):
        x = side * (L.CABIN_HALF_W_HIP + 0.0)
        pts = [(x, L.HALO_Y + 0.05, L.ROCKER_TOP_Z), (x, L.HALO_Y + 0.05, L.SILL_Z + 0.05), (x, y1, 0.86), (x, y1, L.CARGO_FLOOR_Z), (x, L.REAR_BULKHEAD_Y, L.CARGO_FLOOR_Z), (x, L.REAR_BULKHEAD_Y, L.ROCKER_TOP_Z)]
        ring_in = [Vector(p) for p in pts]
        ring_out = [Vector((p[0] + side * 0.03, p[1], p[2])) for p in pts]
        q = lib.loft_object(f'rear.quarter_{side}', [ring_in, ring_out], close_u=True, cap_start=True, cap_end=True, material='carpet_black', uv_scale=2.0, flip=side > 0)
        lib.tag(q, 'rear.quarter.driver' if side < 0 else 'rear.quarter.passenger', 'rear')
    # rear hatch glass from halo top down to the tail, curving in X
    n = 13
    rings = []
    for k in range(5):
        s = k / 4
        y = (L.HALO_Y - 0.06) + (L.REAR_GLASS_END[0] - (L.HALO_Y - 0.06)) * s
        z = (_roof_z(0, L.HALO_Y) + 0.0) + (L.REAR_GLASS_END[1] - _roof_z(0, L.HALO_Y)) * (s ** 1.2)
        hw = L.ROOF_HALF_W + 0.04 * s
        rings.append([Vector((x, y, z - 0.05 * (x / hw) ** 2)) for x in [(-hw + 2 * hw * i / (n - 1)) for i in range(n)]])
    rg = lib.loft_object('glass.rear', rings, close_u=False, material='glass', flip=True)
    lib.tag(rg, 'glass.rear', 'glass', selectable=False)
    # rear glass side rails (trim) to close the gap between glass and quarter panels
    for side in (-1, 1):
        path = [Vector((side * (L.ROOF_HALF_W + 0.04 * s), (L.HALO_Y - 0.06) + (L.REAR_GLASS_END[0] - (L.HALO_Y - 0.06)) * s, _roof_z(0, L.HALO_Y) + (L.REAR_GLASS_END[1] - _roof_z(0, L.HALO_Y)) * (s ** 1.2) - 0.05)) for s in [i / 6 for i in range(7)]]
        r = lib.sweep_tube(f'rear.rail_{side}', path, (0.03, 0.04), n=10, material='plastic_black', up_hint=Vector((1, 0, 0)))
        lib.tag(r, 'rear.rail.driver' if side < 0 else 'rear.rail.passenger', 'rear', selectable=False)


def build_b_pillar_trim():
    for side in (-1, 1):
        x = side * (L.CABIN_HALF_W_SHOULDER - 0.01)
        prof = lib.rounded_rect2d(0.10, L.SILL_Z - L.ROCKER_TOP_Z, 0.02)
        o = lib.extrude_profile(f'pillar.b_{side}', prof, (x, L.HALO_Y, (L.SILL_Z + L.ROCKER_TOP_Z) / 2), (0, 1, 0), (0, 0, 1), side * -0.035, material='plastic_black')
        lib.tag(o, 'pillar.b.driver' if side < 0 else 'pillar.b.passenger', 'pillars')


def build_visors_mirror_overhead():
    slope = Vector((0, L.COWL_Y - L.HEADER_Y, L.COWL_Z - L.HEADER_Z)).normalized()  # down the windshield
    # sun visors stowed flat against the headliner just behind the header, following its curve, hinged at the pillar end
    for side, cid in ((-1, 'roof.visor.driver'), (1, 'roof.visor.passenger')):
        x0, x1, yc, half_y = side * 0.13, side * 0.52, 0.315, 0.068
        rings = []
        xs = _lin(min(x0, x1), max(x0, x1), 16)
        for x in xs:
            e = min(x - xs[0], xs[-1] - x)
            hy = half_y * math.sqrt(max(0.0, 1.0 - (max(0.0, 0.03 - e) / 0.03) ** 2)) if e < 0.03 else half_y
            hy = max(hy, 0.012)
            ring = []
            for (dy, dz) in ((-1, -0.0035), (-0.9, -0.012), (0.9, -0.012), (1, -0.0035)):
                yy = yc + dy * hy
                ring.append(Vector((x, yy, _roof_z(x, yy) + dz - 0.0015)))
            rings.append(ring)
        a_, b_, d_ = rings[3][1], rings[3][2], rings[4][1]
        flip = (b_ - a_).cross(d_ - a_).z > 0
        v = lib.loft_object(cid, rings, close_u=True, cap_start=True, cap_end=True, material='headliner_suede', uv_scale=3.0, flip=flip)
        lib.tag(v, cid, 'roof')
    # rear view mirror: stalk from header + mirror body
    stalk = lib.sweep_tube('mirror.stalk', [Vector((0, L.HEADER_Y + 0.14, L.HEADER_Z - 0.03)), Vector((0, L.HEADER_Y + 0.17, L.HEADER_Z - 0.09)), Vector((0, L.HEADER_Y + 0.18, L.HEADER_Z - 0.13))], 0.012, material='plastic_black')
    lib.tag(stalk, 'mirror.stalk', 'mirror', selectable=False)
    prof = lib.rounded_rect2d(0.26, 0.07, 0.03)
    body = lib.extrude_profile('mirror.body', prof, (0, L.HEADER_Y + 0.17, L.HEADER_Z - 0.17), (1, 0, 0), (0, 0.25, 1), 0.03, material='plastic_black', bevel=0.008)
    lib.tag(body, 'mirror.body', 'mirror')
    glass = lib.extrude_profile('mirror.glass', lib.rounded_rect2d(0.245, 0.058, 0.025), (0, L.HEADER_Y + 0.166, L.HEADER_Z - 0.17), (1, 0, 0), (0, 0.25, 1), -0.002, material='mirror')
    lib.tag(glass, 'mirror.glass', 'mirror', selectable=False)
    # slim map-light module flush with the headliner at the front centre, behind the mirror
    rings = []
    for x in _lin(-0.08, 0.08, 9):
        ring = []
        for (yy, dz) in ((0.36, -0.002), (0.355, -0.011), (0.29, -0.011), (0.285, -0.002)):
            ring.append(Vector((x, yy, _roof_z(x, yy) + dz)))
        rings.append(ring)
    a_, b_, d_ = rings[3][1], rings[3][2], rings[4][1]
    oc = lib.loft_object('roof.overhead_console', rings, close_u=True, cap_start=True, cap_end=True, material='plastic_black', flip=(b_ - a_).cross(d_ - a_).z > 0)
    lib.tag(oc, 'roof.overhead_console', 'roof')
    for side in (-1, 1):
        lamp = lib.revolve('roof.maplight_%d' % side, [(0.0, 0), (0.016, 0), (0.017, 0.002)], segments=20, material='emissive_white', origin=(side * 0.045, 0.322, _roof_z(0, 0.322) - 0.0115), direction=(0, 0, -1))
        lib.tag(lamp, 'lighting.dome.driver' if side < 0 else 'lighting.dome.passenger', 'lighting', selectable=False)


def build_pedals():
    # hanging pedals: arms from under the dash; brake (wide), accelerator (tall narrow), dead pedal on the left
    arm_top = Vector((-0.40, 1.00, 0.48))
    # brake
    brake_face = Vector((-0.42, 0.86, 0.20))
    arm = lib.sweep_tube('pedals.brake_arm', [arm_top, Vector((-0.42, 0.93, 0.34)), brake_face + Vector((0, 0.02, 0.03))], 0.011, material='metal_satin_dark')
    lib.tag(arm, 'pedals.brake_arm', 'pedals', selectable=False)
    bp = lib.extrude_profile('pedals.brake', lib.rounded_rect2d(0.095, 0.065, 0.012), brake_face, (1, 0, 0), (0, -0.35, 1), 0.012, material='rubber', bevel=0.003)
    lib.tag(bp, 'pedals.brake', 'pedals')
    # accelerator
    acc_face = Vector((-0.26, 0.90, 0.16))
    arm2 = lib.sweep_tube('pedals.accel_arm', [Vector((-0.27, 1.02, 0.46)), Vector((-0.26, 0.96, 0.30)), acc_face + Vector((0, 0.02, 0.05))], 0.009, material='metal_satin_dark')
    lib.tag(arm2, 'pedals.accel_arm', 'pedals', selectable=False)
    ap = lib.extrude_profile('pedals.accelerator', lib.rounded_rect2d(0.055, 0.14, 0.012), acc_face, (1, 0, 0), (0, -0.35, 1), 0.012, material='rubber', bevel=0.003)
    lib.tag(ap, 'pedals.accelerator', 'pedals')
    # dead pedal (footrest) on the far left, resting on the toe board
    dp = lib.extrude_profile('pedals.dead_pedal', lib.rounded_rect2d(0.09, 0.18, 0.015), (-0.58, 0.92, 0.22), (1, 0, 0), (0, -0.55, 1), 0.015, material='rubber', bevel=0.003)
    lib.tag(dp, 'pedals.dead_pedal', 'pedals')


def build_kick_panels():
    """Side panels below the dash ends, between door front edge and toe board."""
    for side in (-1, 1):
        x = side * (L.CABIN_HALF_W_HIP + 0.0)
        pts = [(x, L.DOOR_Y_FRONT - 0.02, 0.05), (x, L.DOOR_Y_FRONT - 0.02, L.KNEE_BOLSTER_Z + 0.05), (x - side * 0.03, L.TOEBOARD_Y1, L.KNEE_BOLSTER_Z + 0.08), (x - side * 0.03, L.TOEBOARD_Y1, L.TOEBOARD_Z1 - 0.02)]
        ring_a = [Vector(p) for p in pts]
        ring_b = [Vector((p[0] + side * 0.02, p[1], p[2])) for p in pts]
        o = lib.loft_object(f'trim.kick_{side}', [ring_a, ring_b], close_u=True, cap_start=True, cap_end=True, material='carpet_black', flip=side > 0)
        lib.tag(o, 'trim.kick.driver' if side < 0 else 'trim.kick.passenger', 'trim', selectable=False)


def build():
    build_floor()
    build_rockers()
    build_roof()
    build_halo()
    build_a_pillars_and_glass()
    build_rear()
    build_b_pillar_trim()
    build_visors_mirror_overhead()
    build_pedals()
    build_kick_panels()
