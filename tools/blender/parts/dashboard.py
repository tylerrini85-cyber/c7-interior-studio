"""Dashboard: upper pad with driver instrument hood, centre stack, passenger side, outer vents, cluster, column shroud,
passenger grab handle, trim band, glovebox, switch panels, defroster strip."""
import math
from mathutils import Vector
import lib
import layout as L

# profile templates: 13 control points (y, z) from cowl to under-dash bottom edge
T_DRIVER_OUTER = [(1.08, 0.82), (0.96, 0.845), (0.84, 0.86), (0.72, 0.865), (0.64, 0.86), (0.60, 0.83), (0.60, 0.78), (0.63, 0.72), (0.66, 0.66), (0.69, 0.60), (0.72, 0.54), (0.76, 0.46), (0.82, 0.41)]
T_HOOD = [(1.08, 0.82), (0.96, 0.85), (0.84, 0.875), (0.72, 0.885), (0.63, 0.885), (0.59, 0.87), (0.60, 0.845), (0.73, 0.84), (0.82, 0.76), (0.80, 0.66), (0.72, 0.56), (0.75, 0.46), (0.82, 0.41)]
T_STACK = [(1.08, 0.82), (0.96, 0.845), (0.84, 0.86), (0.72, 0.865), (0.68, 0.862), (0.66, 0.856), (0.655, 0.838), (0.65, 0.77), (0.645, 0.71), (0.64, 0.65), (0.63, 0.61), (0.60, 0.57), (0.55, 0.51)]
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
        x = -0.70 + 1.40 * k / (n - 1)
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
    # (no separate visor: the hood brow is the dash pad itself plus the stitched welt, B21 / B13)
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
    # slim shroud tucked under the hub centre line so nothing shows above the airbag cover from the seat
    prof_small = lib.rounded_rect2d(0.085, 0.060, 0.025)
    prof_big = lib.rounded_rect2d(0.11, 0.07, 0.025)
    u = Vector((1, 0, 0))
    v = axis.cross(u).normalized() * -1  # up-ish
    rings = []
    # kept under the sight line from the eye over the airbag cover (z <= 0.96 - 0.325 * (y + 0.12)) so it stays hidden
    for s, prof, off, drop in ((0.0, prof_small, 0.085, 0.085), (0.45, prof_small, 0.15, 0.11), (1.0, prof_big, 0.26, 0.15)):
        rings.append(lib.place_profile(prof, hub + axis * off - v * drop, u, v))
    col = lib.loft_object('column.shroud', rings, close_u=True, cap_start=True, cap_end=True, material='plastic_black')
    lib.add_bevel(col, 0.012, 4)
    lib.tag(col, 'column.shroud', 'steering')
    # stalks: turn signal (left) and wiper (right)
    for side, cid in ((-1, 'column.stalk.left'), (1, 'column.stalk.right')):
        o = hub + axis * 0.12 - v * 0.085
        path = [o + u * (side * 0.045), o + u * (side * 0.12) + axis * 0.01, o + u * (side * 0.17) + axis * 0.03 - v * 0.005]
        st = lib.sweep_tube(cid, path, 0.011, n=12, radius_fn=lambda t: 0.011 if t < 0.5 else 0.013, material='plastic_black')
        lib.tag(st, cid, 'steering', selectable=False)


# ---------------------------------------------------------------------------
# centre stack: one solid, rearward-leaning body from the dash top down into the console (IMG_4499/4495/4506)
# ---------------------------------------------------------------------------
STACK_CX = 0.01
# (z, y) of the occupant-facing stack surface at the stack centreline, bottom (waterfall into the console) to top
# waterfall at the foot, then one straight plane (slope 0.69) from z 0.60 up to the dash lip (IMG: flat angled stack face)
STACK_FACE = [(0.545, 0.46), (0.552, 0.51), (0.558, 0.55), (0.566, 0.578), (0.60, 0.585), (0.64, 0.594), (0.70, 0.606), (0.76, 0.618), (0.81, 0.628), (0.845, 0.636), (0.852, 0.648)]  # ~80 deg face, waterfall only at the foot
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
    """y of the stack face at lateral x, height z; the face is yawed toward the driver (driver side further forward, passenger side closer to the occupants)."""
    k = 0.6 + 0.4 * max(0.0, min(1.0, (z - 0.552) / 0.025))   # full yaw over the whole flat face
    # STACK_YAW is negative: the driver (-x) end of the face sits further forward (+y), so the face turns toward the driver
    return _interp(STACK_FACE, z) + math.tan(L.STACK_YAW) * (x - STACK_CX) * k


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
    zt = 0.838
    # one wide vent across the left of the stack top, PASS AIR BAG lamp and hazard in a pod on the right (B58 / B21)
    vx, vw, vh = cx - 0.038, 0.190, 0.034
    floor = _panel('dash.vent_center_floor', vw - 0.008, vh - 0.008, vx, zt, 0.001, 0.004, 'plastic_black', 'dashboard', selectable=False, r=0.004)
    lib.tag(floor, 'dash.vents.center.floor', 'dashboard', selectable=False)
    o, u, v, n = stack_frame(vx, zt)
    for j in range(3):
        vane = lib.extrude_profile(f'dash.vent_center_vane{j}', lib.rounded_rect2d(vw - 0.016, 0.0035, 0.0015), o + v * (0.009 - 0.009 * j) + n * 0.0015, u, v, 0.003, material='plastic_black_gloss')
        lib.tag(vane, f'dash.vents.center.vane{j}', 'dashboard', selectable=False)
    knob = lib.box('dash.vent_center_knob', (0.016, 0.005, 0.007), o + n * 0.0045 + u * 0.035, material='plastic_black_gloss')
    lib.tag(knob, 'dash.vents.center.knob', 'dashboard', selectable=False)
    ring = lib.extrude_profile('dash.vent_center', lib.rounded_rect2d(vw, vh, 0.006), o - n * 0.002, u, v, 0.0045, material='metal_brushed')
    hole = lib.extrude_profile('dash.vent_center_hole', lib.rounded_rect2d(vw - 0.008, vh - 0.008, 0.004), o - n * 0.03, u, v, 0.06)
    lib.add_boolean(ring, hole)
    lib.tag(ring, 'dash.vents.center.left', 'dashboard')
    px = cx + 0.112
    pod = _panel('dash.hazard_pod', 0.070, 0.030, px, zt, 0.0025, 0.004, 'plastic_black_gloss', 'dashboard', selectable=False, r=0.005)
    o, u, v, n = stack_frame(px, zt)
    ab = lib.extrude_profile('dash.airbag_lamp', lib.rounded_rect2d(0.030, 0.016, 0.002), o + n * 0.0025 - u * 0.014, u, v, 0.001, material='screen_off')
    lib.tag(ab, 'dash.airbag_lamp', 'electronics', selectable=False)
    hz = lib.extrude_profile('dash.hazard', [Vector((-0.007, -0.005)), Vector((0.007, -0.005)), Vector((0.0, 0.006))], o + n * 0.0025 + u * 0.020, u, v, 0.001, material='emblem')
    lib.tag(hz, 'dash.hazard', 'dashboard', selectable=False)
    # ---- infotainment: gloss surround (wider on the left for the volume knob + SCREEN button), 8-inch screen
    zs_scr = 0.752
    bez = _panel('console.screen_bezel', 0.218, 0.126, cx + 0.028, zs_scr, 0.0012, 0.012, 'plastic_black_gloss', 'console', bevel=0.001, r=0.006)
    scr = _panel('console.screen', 0.190, 0.107, cx + 0.028, zs_scr, 0.0022, 0.001, 'screen_off', 'electronics', r=0.003)
    _panel('console.screen_strip', 0.040, 0.126, cx - 0.105, zs_scr, 0.0012, 0.012, 'plastic_black', 'console', selectable=False, r=0.005)
    _knob('console.volume_knob', cx - 0.105, zs_scr + 0.028, 0.013, 0.012, proud=0.0015)
    _panel('console.screen_btn', 0.026, 0.014, cx - 0.105, zs_scr - 0.012, 0.003, 0.002, 'plastic_black_gloss', 'console', selectable=False, r=0.003)
    _panel('console.screen_btn2', 0.026, 0.014, cx - 0.105, zs_scr - 0.036, 0.003, 0.002, 'plastic_black_gloss', 'console', selectable=False, r=0.003)
    # ---- control block under the screen, laid out from the reference photo:
    #   media row tight under the bezel: RADIO MEDIA home (MENU) prev next BACK, two large knobs at the panel sides
    #   spanning the media row and the first climate row; climate row A: A/C face face+feet rear-defrost SYNC;
    #   climate row B under the middle three: feet feet+defrost front-defrost; badge panel below.
    zc = 0.628
    _panel('console.hvac', 0.310, 0.122, cx, zc, 0.0012, 0.006, 'plastic_black', 'console', r=0.006)
    zm = 0.666
    for k, dx in enumerate((-0.128, 0.128)):
        o, u, v, n = stack_frame(cx + dx, 0.650)
        kn = lib.revolve(f'console.hvac_knob_{k}', [(0, 0), (0.021, 0), (0.021, 0.012), (0.019, 0.016), (0.0, 0.016)], segments=36, material='chrome', origin=o + n * 0.0015, direction=n)
        lib.tag(kn, f'console.hvac_knob.{"left" if k == 0 else "right"}', 'trim', selectable=False)
        cap = lib.revolve(f'console.hvac_knob_cap_{k}', [(0, 0), (0.0165, 0), (0.0165, 0.001), (0.0, 0.001)], segments=36, material='plastic_black', origin=o + n * 0.0175, direction=n)
        lib.tag(cap, f'console.hvac_knob_cap.{k}', 'console', selectable=False)
    # the keys (RADIO MEDIA home MENU prev next BACK / A/C face face+feet rear-defrost SYNC / feet feet+defrost
    # front-defrost) are drawn on the panel by the runtime label texture so they carry their icons and labels
    # CORVETTE badge plate left of centre and a small switch on the right, at the foot of the control panel
    _panel('console.badge_strip', 0.075, 0.011, cx - 0.045, 0.584, 0.0035, 0.004, 'metal_brushed', 'trim', selectable=False, r=0.002)
    _panel('console.foot_switch', 0.030, 0.016, cx + 0.085, 0.584, 0.004, 0.002, 'plastic_black_gloss', 'console', selectable=False, r=0.003)
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


def _vent(cid, x, z, w=0.068, h=0.110, base_proud=0.004, ring_component=None, louvre_h=None):
    """Tall rectangular C7 vent: dark louvre floor just proud of the trim band, three vanes and a slider knob in
    front of it, and a thin bright bezel. Everything sits within a few millimetres of the band so it reads as
    an inset vent rather than a block (IMG_4491 / IMG_4509). nrm points toward the occupant."""
    c, u, v, nrm = _dash_face_frame(x, z)
    floor = lib.extrude_profile(cid, lib.rounded_rect2d(w - 0.010, h - 0.010, 0.006), c + nrm * (base_proud - 0.0005), u, v, 0.001, material='plastic_black')
    lib.tag(floor, cid, 'dashboard')
    top = (h / 2 - 0.012) if louvre_h is None else (h / 2 - 0.012)
    pitch = 0.028 if louvre_h is None else (louvre_h - 0.014) / 2
    for j in range(3):
        vane = lib.extrude_profile(f'{cid}.vane{j}', lib.rounded_rect2d(w - 0.016, 0.0045, 0.0015), c + v * (top - 0.014 - pitch * j) + nrm * (base_proud + 0.001), u, v, 0.0025, material='plastic_black_gloss')
        lib.tag(vane, f'{cid}.vane{j}', 'dashboard', selectable=False)
    knob = lib.box(f'{cid}.knob', (0.016, 0.005, 0.007), c + nrm * (base_proud + 0.0045) + (v * (top - 0.014 - pitch) if louvre_h is not None else Vector((0, 0, 0))), material='plastic_black_gloss')
    lib.tag(knob, f'{cid}.knob', 'dashboard', selectable=False)
    ring = lib.extrude_profile(f'{cid}.ring', lib.rounded_rect2d(w, h, 0.010), c + nrm * (base_proud - 0.004), u, v, 0.0065, material='metal_brushed')
    hole = lib.extrude_profile(f'{cid}.hole', lib.rounded_rect2d(w - 0.010, h - 0.010, 0.006), c - nrm * 0.03, u, v, 0.06)
    lib.add_boolean(ring, hole)
    lib.tag(ring, ring_component or f'{cid}.ring', 'trim', selectable=False)


def build_outer_vents():
    _vent('dash.vents.driver', -0.60, 0.735)
    # passenger inner vent beside the stack is the tall one; the outer vent is shorter with the seat switches
    # directly under it inside the same bezel (IMG_4491 / IMG_4509)
    _vent('dash.vents.passenger_inner', 0.300, 0.735)
    _vent('dash.vents.passenger', 0.585, 0.745, h=0.128, louvre_h=0.070)
    # the two seat switches sit in the lower part of the same bezel
    c, u, v, nrm = _dash_face_frame(0.585, 0.745)
    for k in range(2):
        b = lib.extrude_profile(f'dash.passenger_switch_{k}', lib.rounded_rect2d(0.020, 0.018, 0.003), c + nrm * 0.0065 + u * (-0.014 + 0.028 * k) - v * 0.045, u, v, 0.002, material='plastic_black_gloss')
        lib.tag(b, f'dash.passenger_switch.{k}', 'dashboard', selectable=False)


# passenger hoop centreline (x, y, z): from inside the dash top above the stack's passenger corner, standing out
# from the stack edge with an open gap, bending rearward at the foot into the console's passenger side wall
# (B49 / B37 / B38 / B13)
HOOP_PATH = [
    (0.196, 0.718, 0.846), (0.207, 0.670, 0.842), (0.222, 0.624, 0.826), (0.238, 0.586, 0.792), (0.250, 0.562, 0.742),
    (0.252, 0.548, 0.690), (0.248, 0.534, 0.640), (0.236, 0.506, 0.600), (0.214, 0.458, 0.576), (0.190, 0.392, 0.566),
    (0.166, 0.310, 0.563), (0.154, 0.200, 0.562), (0.150, 0.100, 0.564), (0.150, 0.030, 0.572), (0.150, -0.030, 0.584),
]


def _hoop_profile(w=0.058, h=0.064, r=0.022):
    return lib.rounded_rect2d(w, h, r, n_corner=6)


def build_grab_handle():
    """Passenger grab hoop: a wide leather band (about 46 x 58 mm) that leaves the dash top at the stack's passenger
    corner, stands off the stack with an open gap behind it, and turns rearward at the foot to become the console's
    passenger side bolster. A brushed strip runs down its inboard face (B49 / B37 / B38 / B13)."""
    path = lib.spline_through([Vector(p) for p in HOOP_PATH], n_per_seg=4, tension=0.5)
    def taper(t):
        k = max(0.0, min(1.0, (t - 0.55) / 0.15)); k = k * k * (3 - 2 * k)
        return (1.0 - 0.28 * k, 1.0 - 0.18 * k)
    hoop = lib.sweep_profile('dash.grab', path, _hoop_profile(), material='leather_black', up_hint=Vector((1, 0, 0)), uv_scale=3.0, scale_fn=taper)
    lib.add_bevel(hoop, 0.002, 2)
    lib.tag(hoop, 'dash.grab', 'dashboard')
    # inboard brushed face strip along the upright part (stops where the hoop turns into the console)
    frames = lib.frame_along_path(path, Vector((1, 0, 0)))
    pts, nrms = [], []
    for (o, t, nrm, b) in frames:
        if o.z < 0.585 or o.z > 0.860:
            continue
        inward = -nrm if nrm.x > 0 else nrm
        pts.append(o + inward * 0.0295); nrms.append(inward)
    strip = lib.ribbon('dash.grab_trim', pts, nrms, 0.030, 0.0025, material='metal_brushed', uv_scale=2.0)
    lib.tag(strip, 'dash.grab_trim', 'dashboard')
    # matching driver-side console bolster from the stack foot back to the armrest
    dpath = [Vector((-x, y, z)) for (x, y, z) in HOOP_PATH if y < 0.46]
    dpath = [Vector((-0.160, 0.470, 0.556)), Vector((-0.158, 0.430, 0.561))] + [p for p in dpath if p.y < 0.40]
    dpath = lib.spline_through(dpath, n_per_seg=3, tension=0.5)
    bol = lib.sweep_profile('console.bolster.driver', dpath, _hoop_profile(), material='leather_black', up_hint=Vector((1, 0, 0)), uv_scale=3.0, scale_fn=lambda t: (0.72, 0.82))
    lib.add_bevel(bol, 0.002, 2)
    lib.tag(bol, 'console.bolster.driver', 'console')


def _loft_needs_flip(rings, outward):
    """True when the loft's default winding would face away from `outward` on the first quad."""
    a, b, d = Vector(rings[0][0]), Vector(rings[0][1]), Vector(rings[1][0])
    return (b - a).cross(d - a).dot(Vector(outward)) < 0


def build_trim_band():
    """Mid-dash panels that carry the vents. On the car they are part of the leather dash face: almost flush, no bright
    edges, bounded below by a stitched seam that sweeps up toward the door (IMG_4509 / IMG_4499 / IMG_4491)."""
    specs = (
        (0.215, 0.70, 'dash.trim.passenger', lambda s: 0.645 + 0.045 * s * s, lambda s: 0.790 + 0.025 * s),
        (-0.70, -0.52, 'dash.trim.driver', lambda s: 0.665, lambda s: 0.795),
    )
    for (x0, x1, cid, z_lo_s, z_hi_s) in specs:
        n = 24
        xs = [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]
        sval = (lambda x: (x - x0) / (x1 - x0)) if x1 > 0 else (lambda x: (x1 - x) / (x1 - x0))
        rings = []
        for x in xs:
            s = sval(x); z0, z1 = z_lo_s(s), z_hi_s(s)
            front = []
            for k in range(7):
                z = z0 + (z1 - z0) * k / 6
                front.append(Vector((x, _surface_point(x, z) - 0.0018, z)))
            back = [Vector((x, _surface_point(x, p.z) + 0.004, p.z)) for p in reversed(front)]
            rings.append(front + back)
        band = lib.loft_object(cid, rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=1.5, flip=_loft_needs_flip(rings, (0, -1, 0)))
        lib.tag(band, cid, 'trim')
        # stitched seam bead along the lower edge
        path = []
        for x in xs:
            z = z_lo_s(sval(x))
            path.append(Vector((x, _surface_point(x, z) - 0.0025, z)))
        seam = lib.sweep_tube(f'{cid}.seam', path, 0.0018, n=8, cap=True, material='leather_black', up_hint=Vector((0, 0, 1)))
        lib.tag(seam, f'{cid}.seam', 'dashboard', selectable=False)


def build_glovebox_and_switches():
    # (the C7 has no glovebox in the dash: storage is behind the screen and in the console)
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
    """Stitched brow of the cockpit wrap: from the driver door along the instrument hood's rear edge, across the dash
    lip above the centre stack, and into the top of the passenger hoop (B13 / B38 / B37)."""
    path = []
    n = 22
    for i in range(n):
        x = -0.69 + (STACK_X0 + 0.02 + 0.69) * i / (n - 1)
        prof = lib.spline_through(profile_at(x), n_per_seg=3)
        rear = [p for p in prof if 0.55 < p.x < 0.70]
        pt = max(rear, key=lambda p: p.y) if rear else prof[5]
        path.append(Vector((x, pt.x - 0.003, pt.y + 0.002)))
    # across the stack top: follow the dash lip (rear-most top point of the profile) toward the hoop
    for x in (-0.11, -0.06, 0.0, 0.06, 0.11, 0.15):
        prof = lib.spline_through(profile_at(x), n_per_seg=3)
        top = [p for p in prof if p.y > 0.845 and p.x < 0.72]
        pt = min(top, key=lambda p: p.x) if top else prof[4]
        path.append(Vector((x, pt.x + 0.002, pt.y + 0.002)))
    path.append(Vector(HOOP_PATH[1]) + Vector((0, 0, 0.004)))
    path = lib.spline_through(path, n_per_seg=2)
    welt = lib.sweep_tube('dash.welt', path, 0.0085, n=12, cap=True, material='leather_black', up_hint=Vector((0, 0, 1)), uv_scale=6.0)
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
