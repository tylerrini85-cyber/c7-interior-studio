"""Dashboard: upper pad with driver instrument hood, centre stack, passenger side, outer vents, cluster, column shroud,
passenger grab handle, trim band, glovebox, switch panels, defroster strip."""
import math
from mathutils import Vector
import lib
import layout as L

# profile templates: 13 control points (y, z) from cowl to under-dash bottom edge
T_DRIVER_OUTER = [(1.08, 0.82), (0.96, 0.845), (0.84, 0.86), (0.72, 0.865), (0.64, 0.86), (0.60, 0.83), (0.60, 0.78), (0.63, 0.72), (0.66, 0.66), (0.69, 0.60), (0.72, 0.54), (0.76, 0.46), (0.82, 0.41)]
T_HOOD = [(1.08, 0.82), (0.96, 0.855), (0.84, 0.895), (0.72, 0.915), (0.63, 0.915), (0.585, 0.895), (0.60, 0.86), (0.73, 0.85), (0.82, 0.76), (0.80, 0.66), (0.72, 0.56), (0.75, 0.46), (0.82, 0.41)]
T_STACK = [(1.08, 0.82), (0.96, 0.845), (0.84, 0.86), (0.72, 0.865), (0.68, 0.862), (0.655, 0.856), (0.645, 0.838), (0.62, 0.77), (0.58, 0.71), (0.55, 0.65), (0.52, 0.61), (0.49, 0.57), (0.45, 0.51)]
T_PASS = [(1.08, 0.82), (0.96, 0.845), (0.84, 0.86), (0.72, 0.865), (0.64, 0.86), (0.615, 0.835), (0.61, 0.79), (0.625, 0.73), (0.64, 0.68), (0.66, 0.60), (0.69, 0.52), (0.74, 0.45), (0.82, 0.41)]

STACK_X0, STACK_X1 = -0.165, 0.19


def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def bump(x, c, hw):
    return 1.0 - smoothstep(0.0, 1.0, abs(x - c) / hw)


def profile_at(x):
    w_hood = 1.0 - smoothstep(0.16, 0.27, abs(x - L.CLUSTER_CENTER[0]))
    w_stack = smoothstep(STACK_X0 - 0.03, STACK_X0 + 0.02, x) * (1 - smoothstep(STACK_X1 - 0.02, STACK_X1 + 0.03, x))
    w_pass = smoothstep(STACK_X1, STACK_X1 + 0.12, x)
    w_driver = 1.0 - min(1.0, w_hood + w_stack + w_pass)
    w = [max(0.0, w_driver), w_hood, w_stack, w_pass]
    s = sum(w)
    w = [v / s for v in w]
    pts = []
    for i in range(13):
        y = w[0] * T_DRIVER_OUTER[i][0] + w[1] * T_HOOD[i][0] + w[2] * T_STACK[i][0] + w[3] * T_PASS[i][0]
        z = w[0] * T_DRIVER_OUTER[i][1] + w[1] * T_HOOD[i][1] + w[2] * T_STACK[i][1] + w[3] * T_PASS[i][1]
        # centre stack yaw toward the driver: lower face shifts rearward on the driver side
        if i >= 6:
            y += w[2] * math.tan(-L.STACK_YAW) * (x - STACK_X0) * 0.0  # placeholder (stack object carries the yaw)
        pts.append(Vector((y, z)))
    return pts


def build_upper():
    stations = []
    n = 56
    for k in range(n):
        x = -0.735 + 1.47 * k / (n - 1)
        prof = lib.spline_through(profile_at(x), n_per_seg=3, tension=0.5)
        stations.append([Vector((x, p.x, p.y)) for p in prof])
    obj = lib.loft_object('dash.upper', stations, close_u=False, material='leather_black', uv_scale=1.0, flip=True)
    lib.tag(obj, 'dash.upper', 'dashboard')
    # end caps against the doors (vertical walls) so the dash does not look hollow from the side
    for side, st in ((-1, stations[0]), (1, stations[-1])):
        inner = st
        outer = [Vector((p.x + side * 0.015, p.y, p.z)) for p in st]
        cap = lib.loft_object(f'dash.end_{side}', [inner, outer], close_u=False, material='leather_black', flip=side < 0)
        lib.tag(cap, 'dash.end.driver' if side < 0 else 'dash.end.passenger', 'dashboard', selectable=False)
    # lower closing panel under the dash (dark plastic) from the bottom edge back to the toe board
    bottom = [Vector((st[-1].x, st[-1].y, st[-1].z)) for st in stations]
    toe = [Vector((st[-1].x, L.TOEBOARD_Y1 + 0.02, L.TOEBOARD_Z1 - 0.01)) for st in stations]
    under = lib.loft_object('dash.under', [bottom, toe], close_u=False, material='plastic_black', flip=True)
    lib.tag(under, 'dash.under', 'dashboard', selectable=False)
    return obj


def build_cluster():
    cx, cy, cz = L.CLUSTER_CENTER
    tilt = L.CLUSTER_TILT
    u = Vector((1, 0, 0))
    v = Vector((0, math.sin(tilt), math.cos(tilt)))  # up vector of the cluster face, leaning back
    nrm = u.cross(v)  # (0, -cos, sin): toward the occupant and slightly up
    base = Vector((cx, cy, cz))
    # bezel: rounded rectangle with a wider centre; depth backwards
    bezel_prof = lib.rounded_rect2d(L.CLUSTER_W + 0.04, L.CLUSTER_H + 0.04, 0.035)
    bezel = lib.extrude_profile('cluster.bezel', bezel_prof, base + nrm * 0.0, u, v, -0.05, material='plastic_black', bevel=0.004, bevel_segments=3)
    lib.tag(bezel, 'cluster.bezel', 'cluster')
    # hood lip over the cluster (visor), curved, plastic
    hood_pts = []
    for i in range(9):
        s = i / 8
        x = cx - (L.CLUSTER_W / 2 + 0.03) + (L.CLUSTER_W + 0.06) * s
        hood_pts.append(Vector((x, cy - 0.11 + 0.02 * math.sin(math.pi * s), cz + L.CLUSTER_H / 2 + 0.06)))
    rings = [[p + Vector((0, 0.0, 0.0)) for p in hood_pts], [p + Vector((0, 0.09, 0.015)) for p in hood_pts]]
    visor = lib.loft_object('cluster.hood', rings, close_u=False, material='plastic_black', flip=True)
    lib.add_solidify(visor, 0.006)
    lib.tag(visor, 'cluster.hood', 'cluster')
    # glass face (slightly in front of the bezel)
    glass = lib.extrude_profile('cluster.glass', lib.rounded_rect2d(L.CLUSTER_W, L.CLUSTER_H, 0.025), base - nrm * 0.002, u, v, -0.001, material='screen_off')
    lib.tag(glass, 'cluster.glass', 'cluster', selectable=False)
    # centre 8-inch LCD (0.177 x 0.100 active)
    lcd = lib.extrude_profile('cluster.screen', lib.rounded_rect2d(0.177, 0.100, 0.004), base - nrm * 0.0035, u, v, -0.001, material='screen_off')
    lib.tag(lcd, 'cluster.screen', 'cluster')
    # three "tunnels": a ring around the speedometer, a frame around the LCD, a ring around the right gauges
    for dx, r in ((-0.135, 0.056), (0.125, 0.040)):
        ring = lib.revolve(f'cluster.tunnel_{int(dx * 1000)}', [(r, 0.0), (r + 0.006, 0.0), (r + 0.006, 0.022), (r, 0.022)], segments=40, material='plastic_black', origin=base - nrm * 0.022 + u * dx, direction=-nrm)
        lib.tag(ring, f'cluster.tunnel.{int(dx * 1000)}', 'cluster', selectable=False)
    frame = lib.extrude_profile('cluster.tunnel_center', lib.rounded_rect2d(0.19, 0.112, 0.008), base - nrm * 0.0, u, v, -0.022, material='plastic_black')
    hole = lib.extrude_profile('cluster.tunnel_center_hole', lib.rounded_rect2d(0.182, 0.104, 0.006), base - nrm * 0.03, u, v, 0.06)
    lib.add_boolean(frame, hole)
    lib.tag(frame, 'cluster.tunnel.center', 'cluster', selectable=False)
    # analog speedometer left, fuel + temp right
    spd = lib.revolve('cluster.speedo', [(0.0, 0.0), (0.040, 0.0), (0.044, 0.004)], segments=36, material='screen_off', origin=base - nrm * 0.0035 + u * (-0.135), direction=-nrm)
    lib.tag(spd, 'cluster.speedo', 'cluster')
    for k, (dx, dz) in enumerate(((0.125, 0.030), (0.125, -0.030))):
        g = lib.revolve(f'cluster.gauge_{k}', [(0.0, 0.0), (0.022, 0.0), (0.025, 0.004)], segments=28, material='screen_off', origin=base - nrm * 0.0035 + u * dx + v * dz, direction=-nrm)
        lib.tag(g, 'cluster.fuel' if k == 0 else 'cluster.temp', 'cluster', selectable=False)


def build_column():
    wx, wy, wz = L.WHEEL_CENTER
    tilt = L.WHEEL_TILT
    axis = Vector((0, math.cos(math.radians(16)), math.sin(math.radians(16))))  # column axis into the dash
    hub = Vector((wx, wy, wz))
    prof_small = lib.rounded_rect2d(0.10, 0.075, 0.03)
    prof_big = lib.rounded_rect2d(0.15, 0.115, 0.04)
    u = Vector((1, 0, 0))
    v = axis.cross(u).normalized() * -1  # up-ish
    rings = []
    for s, prof, off, drop in ((0.0, prof_small, 0.055, 0.0), (0.45, prof_small, 0.13, 0.008), (1.0, prof_big, 0.25, 0.03)):
        rings.append(lib.place_profile(prof, hub + axis * off - v * drop, u, v))
    col = lib.loft_object('column.shroud', rings, close_u=True, cap_start=True, cap_end=True, material='plastic_black')
    lib.add_bevel(col, 0.012, 4)
    lib.tag(col, 'column.shroud', 'steering')
    # stalks: turn signal (left) and wiper (right)
    for side, cid in ((-1, 'column.stalk.left'), (1, 'column.stalk.right')):
        o = hub + axis * 0.10
        path = [o + u * (side * 0.05), o + u * (side * 0.12) + axis * 0.01, o + u * (side * 0.17) + axis * 0.03 - v * 0.005]
        st = lib.sweep_tube(cid, path, 0.011, n=12, radius_fn=lambda t: 0.011 if t < 0.5 else 0.013, material='plastic_black')
        lib.tag(st, cid, 'steering', selectable=False)


# ---------------------------------------------------------------------------
# centre stack: one solid, rearward-leaning body from the dash top down into the console (IMG_4499/4495/4506)
# ---------------------------------------------------------------------------
STACK_CX = 0.01
# (z, y) of the occupant-facing stack surface at the stack centreline, bottom (waterfall into the console) to top
# waterfall at the foot, then one straight plane (slope 0.69) from z 0.60 up to the dash lip (IMG: flat angled stack face)
STACK_FACE = [(0.545, 0.395), (0.555, 0.415), (0.575, 0.44), (0.60, 0.47), (0.64, 0.4976), (0.70, 0.539), (0.76, 0.5804), (0.81, 0.6149), (0.845, 0.639), (0.852, 0.652)]
STACK_HALF_W = [(0.545, 0.152), (0.60, 0.156), (0.68, 0.161), (0.76, 0.165), (0.862, 0.168)]


def _interp(table, z):
    if z <= table[0][0]:
        return table[0][1]
    for (z0, v0), (z1, v1) in zip(table, table[1:]):
        if z <= z1:
            t = (z - z0) / (z1 - z0)
            return v0 + (v1 - v0) * t
    return table[-1][1]


def stack_half_w(z):
    return _interp(STACK_HALF_W, z)


def stack_y(x, z):
    """y of the stack face at lateral x, height z; the face is yawed toward the driver (passenger side further forward)."""
    k = 0.6 + 0.4 * max(0.0, min(1.0, (z - 0.555) / 0.045))   # full yaw over the whole flat face
    return _interp(STACK_FACE, z) + math.tan(-L.STACK_YAW) * (x - STACK_CX) * k


def stack_frame(x, z):
    """(origin, u, v, n) on the stack face: u lateral along the face, v up the face, n toward the occupant."""
    h = 0.006
    dydz = (stack_y(x, z + h) - stack_y(x, z - h)) / (2 * h)
    dydx = (stack_y(x + h, z) - stack_y(x - h, z)) / (2 * h)
    u = Vector((1, dydx, 0)).normalized()
    v = Vector((0, dydz, 1)).normalized()
    n = u.cross(v).normalized()
    return Vector((x, stack_y(x, z), z)), u, v, n


def _stack_ring(z, y_front=0.98, r=0.026):
    w = stack_half_w(z)
    pts = []
    n = 17
    for i in range(n):
        x = STACK_CX - w + 2 * w * i / (n - 1)
        y = stack_y(x, z)
        d = abs(x - STACK_CX) - (w - r)
        if d > 0:
            y += r - math.sqrt(max(0.0, r * r - d * d))
        pts.append(Vector((x, y, z)))
    pts.append(Vector((STACK_CX + w, y_front, z)))
    pts.append(Vector((STACK_CX - w, y_front, z)))
    return pts


def _panel(cid, w, h, x, z, proud, depth, material, category='console', selectable=True, bevel=0.0, r=0.006):
    """Rounded-rectangle panel lying on the stack face at (x, z), `proud` metres in front of it, `depth` thick behind."""
    o, u, v, n = stack_frame(x, z)
    obj = lib.extrude_profile(cid, lib.rounded_rect2d(w, h, r), o + n * (proud - depth), u, v, depth, material=material, bevel=bevel)
    lib.tag(obj, cid, category, selectable=selectable)
    return obj


def _knob(cid, x, z, radius, height, material='metal_satin_dark', proud=0.003):
    o, u, v, n = stack_frame(x, z)
    k = lib.revolve(cid, [(0, 0), (radius, 0), (radius, height), (radius - 0.0025, height + 0.002), (0.0, height + 0.002)], segments=32, material=material, origin=o + n * proud, direction=n)
    lib.tag(k, cid, 'console', selectable=False)
    return k


def build_center_stack():
    cx = STACK_CX
    # ---- solid body (leather-wrapped face, closed sides, waterfall into the console)
    zs = [0.545, 0.552, 0.56, 0.572, 0.59, 0.615, 0.645, 0.68, 0.72, 0.76, 0.80, 0.83, 0.845, 0.852]
    rings = [_stack_ring(z, y_front=(0.98 if z < 0.80 else 0.80)) for z in zs]
    body = lib.loft_object('console.stack', rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=1.0)
    lib.tag(body, 'console.stack', 'console')
    # ---- top strip: two slim centre vents with the hazard / passenger-airbag pod between (IMG_4506, 4493)
    zt = 0.826
    for k, dx in enumerate((-0.088, 0.088)):
        side = 'left' if k == 0 else 'right'
        floor = _panel(f'dash.vent_center_{k}_floor', 0.092, 0.030, cx + dx, zt, 0.001, 0.004, 'plastic_black', 'dashboard', selectable=False, r=0.004)
        lib.tag(floor, f'dash.vents.center.{side}.floor', 'dashboard', selectable=False)
        o, u, v, n = stack_frame(cx + dx, zt)
        for j in range(2):
            vane = lib.extrude_profile(f'dash.vent_center_{k}_vane{j}', lib.rounded_rect2d(0.084, 0.004, 0.0015), o + v * (0.006 - 0.012 * j) + n * 0.0015, u, v, 0.003, material='plastic_black_gloss')
            lib.tag(vane, f'dash.vents.center.{k}.vane{j}', 'dashboard', selectable=False)
        knob = lib.box(f'dash.vent_center_{k}_knob', (0.012, 0.004, 0.006), o + n * 0.004, material='plastic_black_gloss')
        lib.tag(knob, f'dash.vents.center.{k}.knob', 'dashboard', selectable=False)
        ring = lib.extrude_profile(f'dash.vent_center_{k}', lib.rounded_rect2d(0.100, 0.038, 0.006), o - n * 0.002, u, v, 0.0045, material='metal_brushed')
        hole = lib.extrude_profile(f'dash.vent_center_{k}_hole', lib.rounded_rect2d(0.092, 0.030, 0.004), o - n * 0.03, u, v, 0.06)
        lib.add_boolean(ring, hole)
        lib.tag(ring, f'dash.vents.center.{side}', 'dashboard')
    pod = _panel('dash.hazard_pod', 0.046, 0.026, cx, zt, 0.0025, 0.004, 'plastic_black_gloss', 'dashboard', selectable=False, r=0.005)
    o, u, v, n = stack_frame(cx, zt)
    hz = lib.extrude_profile('dash.hazard', [Vector((-0.007, -0.005)), Vector((0.007, -0.005)), Vector((0.0, 0.006))], o + n * 0.0025 + u * 0.012, u, v, 0.001, material='emblem')
    lib.tag(hz, 'dash.hazard', 'dashboard', selectable=False)
    ab = lib.extrude_profile('dash.airbag_lamp', lib.rounded_rect2d(0.016, 0.009, 0.002), o + n * 0.0025 - u * 0.010, u, v, 0.001, material='screen_off')
    lib.tag(ab, 'dash.airbag_lamp', 'electronics', selectable=False)
    # ---- infotainment: gloss surround (wider on the left for the volume knob + SCREEN button), 8-inch screen
    zs_scr = 0.752
    bez = _panel('console.screen_bezel', 0.262, 0.168, cx + 0.020, zs_scr, 0.0012, 0.012, 'plastic_black_gloss', 'console', bevel=0.001, r=0.006)
    scr = _panel('console.screen', 0.232, 0.138, cx + 0.020, zs_scr, 0.0022, 0.001, 'screen_off', 'electronics', r=0.003)
    _panel('console.screen_strip', 0.040, 0.168, cx - 0.135, zs_scr, 0.0012, 0.012, 'plastic_black', 'console', selectable=False, r=0.005)
    _knob('console.volume_knob', cx - 0.135, zs_scr + 0.034, 0.014, 0.012, proud=0.0015)
    _panel('console.screen_btn', 0.026, 0.014, cx - 0.135, zs_scr - 0.008, 0.003, 0.002, 'plastic_black_gloss', 'console', selectable=False, r=0.003)
    _panel('console.screen_btn2', 0.026, 0.014, cx - 0.135, zs_scr - 0.034, 0.003, 0.002, 'plastic_black_gloss', 'console', selectable=False, r=0.003)
    # ---- media row: two knobs and five buttons (RADIO, MEDIA, home, MENU, BACK)
    zm = 0.657
    _panel('console.media', 0.310, 0.042, cx, zm, 0.0012, 0.006, 'plastic_black', 'console', r=0.006)
    for k, dx in enumerate((-0.125, 0.125)):
        _knob(f'console.media_knob_{k}', cx + dx, zm, 0.016, 0.012)
    for i in range(5):
        _panel(f'console.media_btn_{i}', 0.030, 0.018, cx - 0.076 + 0.038 * i, zm, 0.0045, 0.002, 'plastic_black_gloss', 'console', selectable=False, r=0.003)
    # ---- climate row: temperature and fan knobs with two button rows between (IMG_4495)
    zh = 0.600
    _panel('console.hvac', 0.310, 0.072, cx, zh, 0.0012, 0.006, 'plastic_black', 'console', r=0.006)
    for k, dx in enumerate((-0.118, 0.118)):
        _knob(f'console.hvac_knob_{k}', cx + dx, zh, 0.025, 0.014)
        o, u, v, n = stack_frame(cx + dx, zh)
        face = lib.revolve(f'console.hvac_lcd_{k}', [(0, 0), (0.018, 0), (0.018, 0.001), (0, 0.001)], segments=32, material='screen_off', origin=o + n * 0.0175, direction=n)
        lib.tag(face, f'console.hvac_lcd.{k}', 'electronics', selectable=False)
    for r in range(2):
        for c in range(4):
            _panel(f'console.hvac_btn_{r}{c}', 0.030, 0.016, cx - 0.054 + 0.036 * c, zh + 0.016 - 0.032 * r, 0.0045, 0.002, 'plastic_black_gloss', 'console', selectable=False, r=0.003)
    # ---- badge lip at the foot of the stack where it turns into the console plate
    _panel('console.badge_strip', 0.200, 0.011, cx, 0.566, 0.002, 0.004, 'metal_brushed', 'trim', selectable=False, r=0.003)
    # ---- engine start button on the driver edge of the stack beside the screen (IMG_4495)
    o, u, v, n = stack_frame(cx - 0.138, 0.700)
    sb = lib.revolve('dash.start_button', [(0, 0), (0.016, 0), (0.016, 0.006), (0.013, 0.008), (0, 0.008)], segments=28, material='metal_satin_dark', origin=o + n * 0.002, direction=n)
    lib.tag(sb, 'dash.start_button', 'dashboard', selectable=False)


def _surface_point(x, z):
    """(y) of the dash surface at lateral x for height z on the rear (occupant) face."""
    prof = lib.spline_through(profile_at(x), n_per_seg=3)
    cand = min([p for p in prof if p.x < 0.75], key=lambda p: abs(p.y - z))
    return cand.x


def _dash_face_frame(x, z):
    """Local frame on the dash's occupant-facing surface at (x, z): u lateral (toed in near the doors), v up along
    the surface, nrm toward the occupant. Used so vents and switch panels lie flat on the trim band."""
    y = _surface_point(x, z)
    c = Vector((x, y, z))
    h = 0.02
    dydz = (_surface_point(x, z + h) - _surface_point(x, z - h)) / (2 * h)
    ang = math.radians(-12 * (1 if x > 0 else -1)) if abs(x) > 0.5 else 0.0
    u = Vector((math.cos(ang), math.sin(ang), 0))
    v = Vector((0, dydz, 1)).normalized()
    nrm = u.cross(v).normalized()
    if nrm.y > 0:
        nrm = -nrm
    return c, u, v, nrm


def _vent(cid, x, z, w=0.068, h=0.110, base_proud=0.010, ring_component=None):
    """Tall rectangular C7 vent: dark louvre floor just proud of the trim band, three vanes and a slider knob in
    front of it, and a thin bright bezel. Everything sits within a few millimetres of the band so it reads as
    an inset vent rather than a block (IMG_4491 / IMG_4509). nrm points toward the occupant."""
    c, u, v, nrm = _dash_face_frame(x, z)
    floor = lib.extrude_profile(cid, lib.rounded_rect2d(w - 0.010, h - 0.010, 0.006), c + nrm * (base_proud - 0.0005), u, v, 0.001, material='plastic_black')
    lib.tag(floor, cid, 'dashboard')
    for j in range(3):
        vane = lib.extrude_profile(f'{cid}.vane{j}', lib.rounded_rect2d(w - 0.016, 0.0045, 0.0015), c + v * (0.028 - 0.028 * j) + nrm * (base_proud + 0.001), u, v, 0.0025, material='plastic_black_gloss')
        lib.tag(vane, f'{cid}.vane{j}', 'dashboard', selectable=False)
    knob = lib.box(f'{cid}.knob', (0.016, 0.005, 0.007), c + nrm * (base_proud + 0.0045), material='plastic_black_gloss')
    lib.tag(knob, f'{cid}.knob', 'dashboard', selectable=False)
    ring = lib.extrude_profile(f'{cid}.ring', lib.rounded_rect2d(w, h, 0.010), c + nrm * (base_proud - 0.004), u, v, 0.0065, material='metal_brushed')
    hole = lib.extrude_profile(f'{cid}.hole', lib.rounded_rect2d(w - 0.010, h - 0.010, 0.006), c - nrm * 0.03, u, v, 0.06)
    lib.add_boolean(ring, hole)
    lib.tag(ring, ring_component or f'{cid}.ring', 'trim', selectable=False)


def build_outer_vents():
    _vent('dash.vents.driver', -0.63, 0.735)
    # passenger inner vent beside the stack is the tall one; the outer vent is shorter with the seat switches
    # directly under it inside the same bezel (IMG_4491 / IMG_4509)
    _vent('dash.vents.passenger_inner', 0.300, 0.735)
    _vent('dash.vents.passenger', 0.645, 0.752, h=0.078)
    c, u, v, nrm = _dash_face_frame(0.645, 0.695)
    sw = lib.extrude_profile('dash.passenger_switches', lib.rounded_rect2d(0.058, 0.030, 0.004), c + nrm * 0.010, u, v, 0.003, material='plastic_black', bevel=0.001)
    lib.tag(sw, 'dash.passenger_switches', 'dashboard', selectable=False)
    for k in range(2):
        b = lib.extrude_profile(f'dash.passenger_switch_{k}', lib.rounded_rect2d(0.020, 0.018, 0.003), c + nrm * 0.013 + u * (-0.014 + 0.028 * k), u, v, 0.002, material='plastic_black_gloss')
        lib.tag(b, f'dash.passenger_switch.{k}', 'dashboard', selectable=False)
    ring = lib.extrude_profile('dash.passenger_switches.ring', lib.rounded_rect2d(0.068, 0.040, 0.008), c + nrm * 0.0095, u, v, 0.003, material='metal_brushed')
    hole = lib.extrude_profile('dash.passenger_switches.hole', lib.rounded_rect2d(0.058, 0.030, 0.004), c - nrm * 0.03, u, v, 0.06)
    lib.add_boolean(ring, hole)
    lib.tag(ring, 'dash.passenger_switches.ring', 'trim', selectable=False)


def build_grab_handle():
    """Passenger grab blade: a thin aluminium ribbon that runs from the dash top down the passenger edge of the
    stack and continues as the passenger edge of the console plate (IMG_4499 / IMG_4506 / IMG_4513)."""
    cx = STACK_CX
    pts, nrms = [], []
    zs = [0.850, 0.835, 0.81, 0.77, 0.73, 0.69, 0.65, 0.615, 0.585, 0.565, 0.552]
    for z in zs:
        x = cx + stack_half_w(z) - 0.020
        o, u, v, n = stack_frame(x, z)
        s = (z - 0.552) / (0.850 - 0.552)
        proud = 0.003 + 0.006 * math.sin(math.pi * s) ** 1.5
        pts.append(o + n * proud); nrms.append(n)
    # then rearward along the passenger edge of the console plate (plate edge x = 0.118)
    for (x, y, z) in ((0.140, 0.40, 0.566), (0.125, 0.355, 0.569), (0.118, 0.28, 0.569), (0.118, 0.05, 0.569), (0.118, -0.08, 0.569)):
        pts.append(Vector((x, y, z))); nrms.append(Vector((0, 0, 1)))
    blade = lib.ribbon('dash.grab_trim', pts, nrms, 0.024, 0.006, material='metal_brushed', uv_scale=2.0)
    lib.tag(blade, 'dash.grab_trim', 'dashboard')


def _loft_needs_flip(rings, outward):
    """True when the loft's default winding would face away from `outward` on the first quad."""
    a, b, d = Vector(rings[0][0]), Vector(rings[0][1]), Vector(rings[1][0])
    return (b - a).cross(d - a).dot(Vector(outward)) < 0


def build_trim_band():
    """Mid-dash trim panels: a sculpted solid band carrying the vents, 6-9 mm proud of the dash pad with a thin
    bright edge top and bottom (IMG_4509/4499: black on the stock car; IMG_4491/4496: carbon overlay). The
    passenger band rises toward the door."""
    for (x0, x1, cid, zb, zt) in ((0.215, 0.735, 'dash.trim.passenger', (0.660, 0.672), (0.790, 0.815)), (-0.735, -0.555, 'dash.trim.driver', (0.665, 0.665), (0.795, 0.795))):
        n = 20
        xs = [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]
        z_lo = lambda x: zb[0] + (zb[1] - zb[0]) * (x - x0) / (x1 - x0)
        z_hi = lambda x: zt[0] + (zt[1] - zt[0]) * (x - x0) / (x1 - x0)
        rings = []
        for x in xs:
            z0, z1 = z_lo(x), z_hi(x)
            outer = []
            for k in range(7):
                t = k / 6
                z = z0 + (z1 - z0) * t
                outer.append(Vector((x, _surface_point(x, z) - 0.006 - 0.003 * math.sin(math.pi * t), z)))
            inner = [Vector((x, _surface_point(x, p.z) + 0.004, p.z)) for p in reversed(outer)]
            rings.append(outer + inner)
        band = lib.loft_object(cid, rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=1.5, flip=_loft_needs_flip(rings, (0, -1, 0)))
        lib.add_bevel(band, 0.003, 2)
        lib.tag(band, cid, 'trim')
        for edge_t, zf in ((0, z_lo), (1, z_hi)):
            path = [Vector((x, _surface_point(x, zf(x)) - 0.0075, zf(x))) for x in xs]
            edge = lib.sweep_tube(f'{cid}.edge{edge_t}', path, 0.0022, n=8, cap=True, material='metal_brushed', up_hint=Vector((0, 0, 1)))
            lib.tag(edge, f'{cid}.edge{edge_t}', 'trim', selectable=False)


def build_glovebox_and_switches():
    # glovebox door outline on the passenger lower dash: a slightly proud panel
    n = 12
    rings = []
    for z in (0.47, 0.50, 0.55, 0.60, 0.64):
        ring = []
        for i in range(n):
            x = 0.30 + 0.38 * i / (n - 1)
            prof = lib.spline_through(profile_at(x), n_per_seg=3)
            cand = min(prof, key=lambda p: abs(p.y - z))
            ring.append(Vector((x, cand.x - 0.004, z)))
        rings.append(ring)
    gb = lib.loft_object('dash.glovebox', rings, close_u=False, material='leather_black', flip=False)
    lib.add_solidify(gb, 0.004, offset=1.0)
    lib.tag(gb, 'dash.glovebox', 'dashboard')
    # driver lower switch panel (headlamp rotary + two buttons)
    base = Vector((-0.615, 0.675, 0.56))
    nrm = Vector((0, -1, 0.25)).normalized()
    u = Vector((1, 0, 0)); v = nrm.cross(u).normalized() * -1
    panel = lib.extrude_profile('dash.switch_panel', lib.rounded_rect2d(0.10, 0.06, 0.008), base, u, v, 0.006, material='plastic_black')
    lib.tag(panel, 'dash.switch_panel', 'dashboard')
    kn = lib.revolve('dash.headlamp_switch', [(0, 0), (0.016, 0), (0.016, 0.012), (0.013, 0.014), (0, 0.014)], segments=24, material='plastic_black_gloss', origin=base - nrm * 0.007 + u * -0.02, direction=-nrm)
    lib.tag(kn, 'dash.headlamp_switch', 'dashboard', selectable=False)
    # defroster grille strip along the cowl and the centre speaker grille
    strip = lib.extrude_profile('dash.defroster', lib.rounded_rect2d(1.25, 0.035, 0.01), (0, 1.015, 0.833), (1, 0, 0), (0, 1, 0.07), -0.006, material='plastic_black')
    lib.tag(strip, 'dash.defroster', 'dashboard', selectable=False)
    spk = lib.extrude_profile('dash.center_speaker', lib.rounded_rect2d(0.16, 0.07, 0.03), (0, 0.90, 0.866), (1, 0, 0), (0, 1, 0.0), -0.003, material='plastic_black')
    lib.tag(spk, 'dash.center_speaker', 'dashboard', selectable=False)


def build_welt():
    """Raised, stitched seam that wraps the driver cockpit: door end -> around the instrument hood -> down the
    driver side of the centre stack to the console."""
    path = []
    # along the hood rear edge (profile point 5 = rear edge crest) from the driver door to the stack
    n = 22
    for i in range(n):
        x = -0.725 + (STACK_X0 - 0.01 + 0.725) * i / (n - 1)
        prof = lib.spline_through(profile_at(x), n_per_seg=3)
        # crest point: max z in the rear half of the top surface
        rear = [p for p in prof if 0.55 < p.x < 0.70]
        pt = max(rear, key=lambda p: p.y) if rear else prof[5]
        path.append(Vector((x, pt.x - 0.003, pt.y + 0.001)))
    # down the driver edge of the stack body
    for z in (0.848, 0.80, 0.74, 0.68, 0.62, 0.575):
        x = STACK_CX - stack_half_w(z) - 0.004
        path.append(Vector((x, stack_y(x + 0.03, z) + 0.006, z)))
    path = lib.spline_through(path, n_per_seg=2)
    welt = lib.sweep_tube('dash.welt', path, 0.0055, n=10, cap=True, material='leather_black', up_hint=Vector((0, 0, 1)), uv_scale=6.0)
    lib.tag(welt, 'dash.welt', 'dashboard')


def build():
    build_upper()
    build_welt()
    build_cluster()
    build_column()
    build_center_stack()
    build_outer_vents()
    build_grab_handle()
    build_trim_band()
    build_glovebox_and_switches()
