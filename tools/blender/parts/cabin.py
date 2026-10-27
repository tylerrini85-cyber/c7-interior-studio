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


def build_roof():
    # headliner (fixed part): side rails strip + front header strip + rear strip; the targa panel is separate
    ys = [L.HEADER_Y, 0.34, L.TARGA_Y_FRONT]
    def ring_at(y, half_w, n=17):
        return [Vector((x, y, _roof_z(x, y))) for x in [(-half_w + 2 * half_w * i / (n - 1)) for i in range(n)]]
    # front header pad
    rings = [ring_at(y, L.ROOF_HALF_W) for y in (L.HEADER_Y - 0.02, L.HEADER_Y + 0.03, L.TARGA_Y_FRONT)]
    front = lib.loft_object('roof.header', rings, close_u=False, material='headliner_suede', uv_scale=2.0)
    lib.tag(front, 'roof.header', 'roof')
    # rear strip between targa panel and halo
    rings = [ring_at(y, L.ROOF_HALF_W) for y in (L.TARGA_Y_REAR, L.HALO_Y + 0.06)]
    rear = lib.loft_object('roof.rear_strip', rings, close_u=False, material='headliner_suede', uv_scale=2.0)
    lib.tag(rear, 'roof.rear_strip', 'roof')
    # side rails (between targa edge and roof edge), both sides
    for side in (-1, 1):
        xs = [side * L.TARGA_HALF_W, side * (L.TARGA_HALF_W + 0.06), side * L.ROOF_HALF_W]
        rings = []
        for y in (L.TARGA_Y_FRONT, 0.0, L.TARGA_Y_REAR):
            rings.append([Vector((x, y, _roof_z(x, y) - (0.0 if abs(x) < L.TARGA_HALF_W + 0.001 else 0.0))) for x in xs])
        rail = lib.loft_object(f'roof.rail_{side}', rings, close_u=False, material='headliner_suede', uv_scale=2.0, flip=False)
        lib.tag(rail, 'roof.rail.driver' if side < 0 else 'roof.rail.passenger', 'roof')
    # removable targa panel headliner (slightly recessed by a seam)
    n = 17
    rings = []
    for y in (L.TARGA_Y_FRONT - 0.008, 0.1, -0.1, L.TARGA_Y_REAR + 0.008):
        hw = L.TARGA_HALF_W - 0.008
        rings.append([Vector((x, y, _roof_z(x, y) - 0.006)) for x in [(-hw + 2 * hw * i / (n - 1)) for i in range(n)]])
    panel = lib.loft_object('roof.panel', rings, close_u=False, material='headliner_suede', uv_scale=2.0)
    lib.tag(panel, 'roof.panel', 'roof')
    # seam channel around the panel (dark plastic) built as a thin frame
    outer = lib.rounded_rect2d(2 * L.TARGA_HALF_W + 0.02, L.TARGA_Y_FRONT - L.TARGA_Y_REAR + 0.02, 0.03)
    frame_rings = []
    for z_off in (0.0, -0.012):
        ring = []
        for p in outer:
            y = (L.TARGA_Y_FRONT + L.TARGA_Y_REAR) / 2 + p.y
            ring.append(Vector((p.x, y, _roof_z(p.x, y) + z_off)))
        frame_rings.append(ring)
    # frame as a lofted band of two rings is just a wall; good enough for a seam shadow
    seam = lib.loft_object('roof.seam', frame_rings, close_u=True, material='plastic_black')
    lib.tag(seam, 'roof.seam', 'roof', selectable=False)


def build_halo():
    """B-pillar hoop: arch over the roof at HALO_Y down to the rockers on both sides."""
    path = []
    n = 24
    for i in range(n + 1):
        t = i / n
        # parametric arch: sides go up vertically then curve over the roof
        if t < 0.25:
            s = t / 0.25
            x = -L.CABIN_HALF_W_SHOULDER + 0.03
            z = L.ROCKER_TOP_Z + (L.SILL_Z - L.ROCKER_TOP_Z) * s
        elif t > 0.75:
            s = (t - 0.75) / 0.25
            x = L.CABIN_HALF_W_SHOULDER - 0.03
            z = L.SILL_Z - (L.SILL_Z - L.ROCKER_TOP_Z) * s
        else:
            s = (t - 0.25) / 0.5
            a = math.pi * (1 - s)
            x = (L.CABIN_HALF_W_SHOULDER - 0.03) * math.cos(a) * -1 * -1
            x = -(L.CABIN_HALF_W_SHOULDER - 0.03) * math.cos(math.pi * s)
            # ellipse from sill height up to roof
            z = L.SILL_Z + (_roof_z(x, L.HALO_Y) - 0.02 - L.SILL_Z) * math.sin(math.pi * s) ** 0.6
        path.append(Vector((x, L.HALO_Y, z)))
    halo = lib.sweep_tube('pillar.halo', path, (0.045, 0.055), n=12, cap=True, material='suede_black', up_hint=Vector((0, 1, 0)), uv_scale=2.0)
    lib.tag(halo, 'pillar.halo', 'pillars')


def build_a_pillars_and_glass():
    for side in (-1, 1):
        base = Vector((side * L.WINDSHIELD_HALF_W_BASE, L.COWL_Y, L.COWL_Z))
        top = Vector((side * L.WINDSHIELD_HALF_W_TOP, L.HEADER_Y, L.HEADER_Z))
        path = [base + (top - base) * (i / 6) for i in range(7)]
        # pillar slightly bowed outward in the middle
        for i, p in enumerate(path):
            s = i / 6
            p.x += side * 0.02 * math.sin(math.pi * s)
        pil = lib.sweep_tube(f'pillar.a_{side}', path, (0.055, 0.045), n=12, cap=True, material='suede_black', up_hint=Vector((1, 0, 0)), uv_scale=2.0)
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
    # header bar (roof front edge) - padded trim between windshield top and the headliner
    prof = lib.rounded_rect2d(0.06, 0.05, 0.02)
    hdr = lib.extrude_profile('pillar.header', prof, (-L.WINDSHIELD_HALF_W_TOP, L.HEADER_Y, L.HEADER_Z - 0.01), (0, 1, 0), (0, 0, 1), 2 * L.WINDSHIELD_HALF_W_TOP, material='suede_black')
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
    for side, cid in ((-1, 'roof.visor.driver'), (1, 'roof.visor.passenger')):
        prof = lib.rounded_rect2d(0.40, 0.14, 0.04)
        center = Vector((side * 0.36, L.HEADER_Y + 0.09, L.HEADER_Z - 0.045))
        v = lib.extrude_profile(cid, prof, center, (1, 0, 0), slope, 0.018, material='headliner_suede', bevel=0.006)
        lib.tag(v, cid, 'roof')
    # rear view mirror: stalk from header + mirror body
    stalk = lib.sweep_tube('mirror.stalk', [Vector((0, L.HEADER_Y + 0.14, L.HEADER_Z - 0.03)), Vector((0, L.HEADER_Y + 0.17, L.HEADER_Z - 0.09)), Vector((0, L.HEADER_Y + 0.18, L.HEADER_Z - 0.13))], 0.012, material='plastic_black')
    lib.tag(stalk, 'mirror.stalk', 'mirror', selectable=False)
    prof = lib.rounded_rect2d(0.26, 0.07, 0.03)
    body = lib.extrude_profile('mirror.body', prof, (0, L.HEADER_Y + 0.17, L.HEADER_Z - 0.17), (1, 0, 0), (0, 0.25, 1), 0.03, material='plastic_black', bevel=0.008)
    lib.tag(body, 'mirror.body', 'mirror')
    glass = lib.extrude_profile('mirror.glass', lib.rounded_rect2d(0.245, 0.058, 0.025), (0, L.HEADER_Y + 0.166, L.HEADER_Z - 0.17), (1, 0, 0), (0, 0.25, 1), -0.002, material='mirror')
    lib.tag(glass, 'mirror.glass', 'mirror', selectable=False)
    # overhead console (map lights) at header centre behind the mirror
    oc = lib.extrude_profile('roof.overhead_console', lib.rounded_rect2d(0.22, 0.12, 0.03), (0, L.HEADER_Y - 0.02, _roof_z(0, L.HEADER_Y) - 0.001), (1, 0, 0), (0, 1, 0), -0.02, material='plastic_black', bevel=0.005)
    lib.tag(oc, 'roof.overhead_console', 'roof')
    for side in (-1, 1):
        lamp = lib.revolve('roof.maplight_%d' % side, [(0.0, 0), (0.018, 0), (0.02, 0.004)], segments=20, material='emissive_white', origin=(side * 0.07, L.HEADER_Y - 0.02, _roof_z(0, L.HEADER_Y) - 0.021), direction=(0, 0, -1))
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
