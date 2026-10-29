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

STACK_X0, STACK_X1 = -0.135, 0.14


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


# cluster layout in the cluster face plane (u right, v up, metres from CLUSTER_CENTER), measured from B41 / B21 / B13:
# two physical side gauges whose dial arcs wrap the outer edges, needles pivoting beside the centre display
CL_DISPLAY = (0.0, 0.012, 0.178, 0.110)        # centre display opening (u, v, w, h)
CL_PIVOT_L = (-0.128, -0.017)                  # speedometer pivot
CL_PIVOT_R = (0.128, -0.012)                   # fuel / coolant pivot
CL_POD_R = 0.066                               # radius of the side pod windows around their pivots
CL_POD_EDGE = 0.092                            # |u| of the straight inner edge of the side pod windows
CL_GLASS = (0.380, 0.170, -0.005)              # dial face / display plane (w, h, v centre); texture is 1140 x 510 px


def _pod_outline(pivot, side):
    """D-shaped window, counter-clockwise: the outer arc of a CL_POD_R circle around the pivot, closed by a straight
    edge at |u| = CL_POD_EDGE on the display side."""
    px, pv = pivot
    a = math.acos(abs(side * CL_POD_EDGE - px) / CL_POD_R)
    t0, t1 = (a, 2 * math.pi - a) if side < 0 else (math.pi + a, 3 * math.pi - a)
    n = 32
    return [Vector((px + CL_POD_R * math.cos(t0 + (t1 - t0) * i / n), pv + CL_POD_R * math.sin(t0 + (t1 - t0) * i / n))) for i in range(n + 1)]


def build_cluster():
    cx, cy, cz = L.CLUSTER_CENTER
    tilt = L.CLUSTER_TILT
    u = Vector((1, 0, 0))
    v = Vector((0, math.sin(tilt), math.cos(tilt)))  # up vector of the cluster face, leaning back
    nrm = u.cross(v)  # toward the occupant and slightly up
    base = Vector((cx, cy, cz))
    # binnacle face: one dark moulding with three openings (left pod, display, right pod); the openings become
    # short tunnels because the moulding is 45 mm deep
    bezel = lib.extrude_profile('cluster.bezel', lib.rounded_rect2d(0.410, 0.190, 0.040), base + v * (-0.008), u, v, -0.045, material='plastic_black', bevel=0.004, bevel_segments=3)
    du, dv, dw, dh = CL_DISPLAY
    # cutters are extruded with a positive depth (a negative depth turns them inside out and the boolean does nothing)
    cut = lib.extrude_profile('cluster.cut_display', lib.rounded_rect2d(dw, dh, 0.008, offset=(du, dv)), base - nrm * 0.08, u, v, 0.10)
    lib.add_boolean(bezel, cut)
    for side, pivot in ((-1, CL_PIVOT_L), (1, CL_PIVOT_R)):
        c2 = lib.extrude_profile(f'cluster.cut_pod_{side}', _pod_outline(pivot, side), base - nrm * 0.08, u, v, 0.10)
        lib.add_boolean(bezel, c2)
    lib.tag(bezel, 'cluster.bezel', 'cluster')
    # dial faces and display: one textured plane at the back of the tunnels (the runtime draws all three gauges)
    gw, gh, gv = CL_GLASS
    glass = lib.extrude_profile('cluster.glass', lib.rounded_rect2d(gw, gh, 0.004), base + v * gv - nrm * 0.026, u, v, -0.001, material='screen_off')
    lib.tag(glass, 'cluster.glass', 'cluster', selectable=False)
    # needle hubs: small dark caps on the side pivots, standing just off the dial faces
    for side, (px, pv) in ((-1, CL_PIVOT_L), (1, CL_PIVOT_R)):
        hub = lib.revolve(f'cluster.hub_{side}', [(0.0, 0.0), (0.008, 0.0), (0.008, 0.004), (0.006, 0.006), (0.0, 0.006)], segments=24, material='plastic_black_gloss', origin=base + u * px + v * pv - nrm * 0.025, direction=nrm)
        lib.tag(hub, f'cluster.hub.{side}', 'cluster', selectable=False)


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
STACK_CX = 0.0
# (z, y) of the occupant-facing stack surface at the stack centreline, bottom (waterfall into the console) to top
# waterfall at the foot, then one straight plane (slope 0.69) from z 0.60 up to the dash lip (IMG: flat angled stack face)
STACK_FACE = [(0.545, 0.46), (0.552, 0.51), (0.558, 0.55), (0.566, 0.578), (0.60, 0.585), (0.64, 0.594), (0.70, 0.606), (0.76, 0.618), (0.81, 0.628), (0.845, 0.636), (0.852, 0.648)]  # ~80 deg face, waterfall only at the foot
STACK_HALF_W = [(0.545, 0.108), (0.60, 0.112), (0.68, 0.118), (0.76, 0.123), (0.862, 0.127)]   # narrow enough for the seats


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
    # ---- top opening (B58 / B21 / B36 / B56): one long tapered opening under the brow, tall and round at the
    # driver end and narrowing to the passenger end; louvres fill the left part, the PASS AIR BAG lamp module and the
    # hazard button sit in the narrow right part. Its walls are lined, its edge has a thin bright rim, and every
    # outline point is projected onto the (curved) stack face so nothing floats or sinks.
    _stack_top_opening(cx)
    # ---- infotainment: gloss surround (wider on the left for the volume knob + SCREEN button), 8-inch screen
    zs_scr = 0.749
    bez = _panel('console.screen_bezel', 0.180, 0.118, cx + 0.020, zs_scr, 0.0012, 0.012, 'plastic_black_gloss', 'console', bevel=0.001, r=0.006)
    scr = _panel('console.screen', 0.158, 0.092, cx + 0.020, zs_scr, 0.0022, 0.001, 'screen_off', 'electronics', r=0.003)
    _panel('console.screen_strip', 0.034, 0.118, cx - 0.094, zs_scr, 0.0012, 0.012, 'plastic_black', 'console', selectable=False, r=0.005)
    _knob('console.volume_knob', cx - 0.094, zs_scr + 0.030, 0.012, 0.012, proud=0.0015)
    _panel('console.screen_btn', 0.024, 0.013, cx - 0.094, zs_scr - 0.008, 0.003, 0.002, 'plastic_black_gloss', 'console', selectable=False, r=0.003)
    # ---- control block under the screen, laid out from the reference photo:
    #   media row tight under the bezel: RADIO MEDIA home (MENU) prev next BACK, two large knobs at the panel sides
    #   spanning the media row and the first climate row; climate row A: A/C face face+feet rear-defrost SYNC;
    #   climate row B under the middle three: feet feet+defrost front-defrost; badge panel below.
    zc = 0.628
    _panel('console.hvac', 0.232, 0.122, cx, zc, 0.0012, 0.006, 'plastic_black', 'console', r=0.006)
    # Everything below is placed in the panel's own frame (along-face mm from the panel centre), which is exactly how
    # the runtime label texture (controlPanelTexture) maps onto the panel, so caps and labels line up.
    po, pu, pv, pn = stack_frame(cx, zc)
    PANEL_FRONT = 0.0012
    CAP = 0.0030                                         # key travel above the panel face

    def at(x_mm, z_mm, proud):
        return po + pu * (x_mm / 1000) + pv * ((z_mm - 628) / 1000) + pn * proud
    for k, x_mm in enumerate((-97, 97)):
        c0 = at(x_mm, 650, 0.0015)
        kn = lib.revolve(f'console.hvac_knob_{k}', [(0, 0), (0.0165, 0), (0.0165, 0.012), (0.0148, 0.016), (0.0, 0.016)], segments=36, material='chrome', origin=c0, direction=pn)
        lib.tag(kn, f'console.hvac_knob.{"left" if k == 0 else "right"}', 'trim', selectable=False)
        cap = lib.revolve(f'console.hvac_knob_cap_{k}', [(0, 0), (0.0128, 0), (0.0128, 0.001), (0.0, 0.001)], segments=36, material='plastic_black', origin=c0 + pn * 0.016, direction=pn)
        lib.tag(cap, f'console.hvac_knob_cap.{k}', 'console', selectable=False)
    # raised key caps (B58 / B21): media row RADIO MEDIA home (MENU) prev next BACK; two climate rows of six
    keys = [(-58.5 + 19.5 * i, 666, 17, 13) for i in range(7) if i != 3]
    keys += [((-59.5 + 19.5 * i) if i < 3 else (20.5 + 19.5 * (i - 3)), z, 17, 14) for z in (636, 613) for i in range(6)]
    for j, (x_mm, z_mm, w_mm, h_mm) in enumerate(keys):
        kc = lib.extrude_profile(f'console.key_{j}', lib.rounded_rect2d(w_mm / 1000, h_mm / 1000, 0.0025), at(x_mm, z_mm, PANEL_FRONT), pu, pv, CAP, material='plastic_black_gloss', bevel=0.0008, bevel_segments=2)
        lib.tag(kc, f'console.key.{j}', 'console', selectable=False)
    menu = lib.revolve('console.key_menu', [(0, 0), (0.0095, 0), (0.0095, CAP - 0.0006), (0.0088, CAP), (0.0, CAP)], segments=36, material='plastic_black_gloss', origin=at(0, 666, PANEL_FRONT), direction=pn)
    lib.tag(menu, 'console.key.menu', 'console', selectable=False)
    # chrome Y between the climate halves: arms rise toward the media row, stem drops below the second row
    ypath = [at(-8.5, 650, PANEL_FRONT + 0.0016), at(0, 625, PANEL_FRONT + 0.0016), at(8.5, 650, PANEL_FRONT + 0.0016)]
    y1 = lib.sweep_tube('console.climate_y_arms', ypath, 0.0017, n=10, cap=True, material='chrome', up_hint=pn)
    lib.tag(y1, 'console.climate_y.arms', 'trim', selectable=False)
    y2 = lib.sweep_tube('console.climate_y_stem', [at(0, 625, PANEL_FRONT + 0.0016), at(0, 600, PANEL_FRONT + 0.0016)], 0.0017, n=10, cap=True, material='chrome', up_hint=pn)
    lib.tag(y2, 'console.climate_y.stem', 'trim', selectable=False)
    # CORVETTE badge plate left of centre and a small switch on the right, at the foot of the control panel
    _panel('console.badge_strip', 0.062, 0.011, cx - 0.038, 0.584, 0.0035, 0.004, 'metal_brushed', 'trim', selectable=False, r=0.002)
    _panel('console.foot_switch', 0.026, 0.016, cx + 0.070, 0.584, 0.004, 0.002, 'plastic_black_gloss', 'console', selectable=False, r=0.003)
    # ---- engine start button on the driver edge of the stack beside the screen (IMG_4495)
    # (in the bottom of the button column left of the screen, under the SCREEN key)
    o, u, v, n = stack_frame(cx - 0.094, zs_scr - 0.036)
    sb = lib.revolve('dash.start_button', [(0, 0), (0.0125, 0), (0.0125, 0.005), (0.010, 0.007), (0, 0.007)], segments=28, material='metal_satin_dark', origin=o + n * 0.002, direction=n)
    lib.tag(sb, 'dash.start_button', 'dashboard', selectable=False)


TOP_OPEN_Z = 0.831                      # frame height of the stack-top opening
# outline (mm, along the face from the frame centre): flat bottom, top following the brow down toward the passenger
# end, a round driver end and a tight passenger end
TOP_OPEN = [(-94, -19), (99, -19), (99, -7), (6, 15), (-90, 20)]
TOP_OPEN_R = [13, 4, 3, 24, 13]


def _rounded_poly_r(corners, radii, n=6):
    """_rounded_poly with a radius per corner."""
    out = []
    m = len(corners)
    for i in range(m):
        p, a, b = corners[i], corners[i - 1], corners[(i + 1) % m]
        r = radii[i]
        e1, e2 = (a - p).normalized(), (b - p).normalized()
        th = math.acos(max(-1.0, min(1.0, e1.dot(e2))))
        t = r / math.tan(th / 2)
        cen = p + (e1 + e2).normalized() * (r / math.sin(th / 2))
        t1, t2 = p + e1 * t, p + e2 * t
        a1 = math.atan2(t1.y - cen.y, t1.x - cen.x)
        a2 = math.atan2(t2.y - cen.y, t2.x - cen.x)
        while a2 < a1:
            a2 += 2 * math.pi
        for k in range(n + 1):
            ang = a1 + (a2 - a1) * k / n
            out.append(Vector((cen.x + r * math.cos(ang), cen.y + r * math.sin(ang))))
    return out


def _top_outline(d_mm=0.0):
    """Stack-top opening outline in metres, moved inward by d_mm (outward when negative)."""
    pts = [Vector((u / 1000, v / 1000)) for u, v in TOP_OPEN]
    if d_mm:
        pts = _offset_poly(pts, d_mm / 1000)
    return _rounded_poly_r(pts, [max(0.001, (r - d_mm) / 1000) for r in TOP_OPEN_R])


def _stack_face_pt(o, u, v, p2, proud):
    """Point on the stack face under the frame point o + u*p.x + v*p.y, `proud` metres in front of the face."""
    q = o + u * p2.x + v * p2.y
    return Vector((q.x, stack_y(q.x, q.z) - proud, q.z))


def _stack_top_opening(cx):
    o, u, v, n = stack_frame(cx, TOP_OPEN_Z)
    hole = _top_outline()
    cutter = lib.extrude_profile('dash.vent_center_cut', hole, o - n * 0.04, u, v, 0.07)
    lib.add_boolean(bpy_obj('console.stack'), cutter)
    # lining: walls 0.4 mm inside the cut, facing the opening, closed by a dark back 18 mm in
    liner = _top_outline(0.4)
    front = [_stack_face_pt(o, u, v, p, 0.0006) for p in liner]
    back = [f + Vector((0, 0.018, 0)) for f in front]
    walls = lib.loft_object('dash.vent_center_floor', [front, back], close_u=True, cap_end=True, material='plastic_black', flip=_loft_needs_flip([front, back], o - front[0]))
    lib.tag(walls, 'dash.vents.center.floor', 'dashboard', selectable=False)
    # thin dark gloss lip around the opening (no bright bezel on the car): 2 mm wide, 1 mm proud, conforming to the face
    ro, ri = _top_outline(-2.0), _top_outline(0.6)
    rings = [[_stack_face_pt(o, u, v, p, pr) for p in pts] for pts, pr in ((ro, 0.001), (ri, 0.001), (ri, -0.002), (ro, -0.002), (ro, 0.001))]
    rim = lib.loft_object('dash.vent_center', rings, close_u=True, material='plastic_black_gloss', flip=_loft_needs_flip(rings, n))
    lib.tag(rim, 'dash.vents.center.lip', 'dashboard', selectable=False)

    def width_at(vv, x_max=1.0):
        xs = []
        for i in range(len(hole)):
            a, b = hole[i], hole[(i + 1) % len(hole)]
            if (a.y - vv) * (b.y - vv) <= 0 and a.y != b.y:
                xs.append(a.x + (b.x - a.x) * (vv - a.y) / (b.y - a.y))
        return (min(xs), min(max(xs), x_max)) if len(xs) >= 2 else (0.0, 0.0)

    def panel(cid, x0, x1, v0, v1, depth, material, r=0.002):
        """Flat part inside the opening spanning u x0..x1, v v0..v1 (m), its front `depth` behind the face."""
        cu, cv = (x0 + x1) / 2, (v0 + v1) / 2
        c = _stack_face_pt(o, u, v, Vector((cu, cv)), -depth)
        obj = lib.extrude_profile(cid, lib.rounded_rect2d(x1 - x0, v1 - v0, r), c - n * 0.004, u, v, 0.004, material=material)
        lib.tag(obj, cid, 'dashboard', selectable=False)
        return c
    # louvres across the driver part of the opening, tipped down toward the occupant, with a chrome slider tab
    for j, vv in enumerate((0.0105, 0.0010, -0.0085)):
        x0, x1 = width_at(vv, x_max=0.019)
        c = _stack_face_pt(o, u, v, Vector(((x0 + x1) / 2, vv)), -0.006)
        vane = lib.extrude_profile(f'dash.vent_center_vane{j}', lib.rounded_rect2d(x1 - x0 - 0.003, 0.0032, 0.0012), c, u, (v * 0.94 + n * 0.34).normalized(), 0.0016, material='plastic_black_gloss')
        lib.tag(vane, f'dash.vents.center.vane{j}', 'dashboard', selectable=False)
    tab = _stack_face_pt(o, u, v, Vector((-0.024, 0.0005)), -0.0035)
    knob = lib.extrude_profile('dash.vent_center_knob', lib.rounded_rect2d(0.020, 0.006, 0.002), tab - n * 0.002, u, v, 0.004, material='chrome')
    lib.tag(knob, 'dash.vents.center.knob', 'dashboard', selectable=False)
    # PASS AIR BAG lamp module and the hazard button in the narrow passenger part
    c = panel('dash.hazard_pod', 0.024, 0.069, -0.0155, 0.0060, 0.0015, 'plastic_black_gloss')
    ab = lib.extrude_profile('dash.airbag_lamp', lib.rounded_rect2d(0.024, 0.011, 0.0015), c + u * 0.003 + v * 0.001, u, v, 0.0006, material='screen_off')
    lib.tag(ab, 'dash.airbag_lamp', 'electronics', selectable=False)
    c = panel('dash.hazard_button', 0.073, 0.095, -0.0155, -0.0030, 0.0010, 'plastic_black_gloss')
    hz = lib.extrude_profile('dash.hazard', [Vector((-0.0055, -0.0035)), Vector((0.0055, -0.0035)), Vector((0.0, 0.0045))], c, u, v, 0.0007, material='emblem')
    lib.tag(hz, 'dash.hazard', 'dashboard', selectable=False)


def bpy_obj(name):
    import bpy
    return bpy.data.objects[name]


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
    _vent('dash.vents.driver', -0.652, 0.735)
    # the passenger vents are recessed into the passenger pad (build_passenger_pad)


# ---------------------------------------------------------------------------
# passenger grab wing (B13 / B21 / B37 / B16 / owner photo of the slot): a fin standing rearward off the stack's
# passenger edge and facing the driver (B38 shows it as a thin silver line beside the band), narrow at the top and
# widening downward, with a long teardrop grab slot through its lower half. Its outer edge is the leather band of the
# cockpit wrap, which carries on in the same line along the console's passenger edge into the armrest; the fin runs
# down into the console top, and its passenger-facing back is leather (the colour seen through the slot).
# ---------------------------------------------------------------------------
WING_DIR = Vector((0.20, -1.0, 0.0)).normalized()    # away from the stack edge: almost straight toward the occupants


def _stack_edge(z):
    x = STACK_CX + stack_half_w(z) - 0.002
    return Vector((x, stack_y(x, z) + 0.004, z))


def _wing_width(z):
    """Brushed face width measured from the stack edge to the roll: ~22 mm at the top, ~58 mm at the slot."""
    t = max(0.0, min(1.0, (0.850 - z) / 0.230))
    return 0.028 + 0.032 * (t * t * (3 - 2 * t))



# ---------------------------------------------------------------------------
# Passenger bar (B38 / B13 / B49 / B37): a wide, flat-faced leather band. It starts inside the dash top, runs down
# the stack's passenger edge tucked over the brushed wing's outer edge, bends rearward at the foot in one smooth
# sweep, and becomes the tall padded passenger side of the console running into the armrest. The driver side of
# the console carries the same bolster. All sections come from _band_ring so there are no seams or lumps.
# ---------------------------------------------------------------------------
BAND_UP = (0.023, 0.013)     # upright: half width along WING_DIR, half thickness toward the cabin
BAND_CON = (0.2115, 0.012)   # console: nominal half height of the padded side wall (its bottom follows the carpet), half width
                             # (about the upright's thickness, so the band reads as one even strip from above)
CON_TOP = 0.025              # console side wall rises this far above the band's centre line
CON_X_DRV, CON_Z = L.CONSOLE_HALF_W + 0.002, 0.558  # driver console bolster centre line (|x|) and the bolsters' centre height
BEND_Z0, BEND_Z1 = 0.612, 0.552


def _floor_z(x, y):
    """Carpet height at (x, y): the cabin floor section with its tunnel hump, lifted by the toe board (cabin.py)."""
    zb = 0.0 if y <= L.TOEBOARD_Y0 else L.TOEBOARD_Z1 * min(1.0, (y - L.TOEBOARD_Y0) / (L.TOEBOARD_Y1 - L.TOEBOARD_Y0)) ** 1.4
    t, tz = L.TUNNEL_HALF_W, L.TUNNEL_Z + zb
    prof = [(0.0, tz + 0.01), (t - 0.03, tz), (t, tz - 0.06), (t + 0.03, zb + 0.03), (t + 0.10, zb)]
    ax = abs(x)
    if ax >= prof[-1][0]:
        return zb
    for (x0, z0), (x1, z1) in zip(prof, prof[1:]):
        if ax <= x1:
            return z0 + (z1 - z0) * (ax - x0) / (x1 - x0)
    return zb


def _wall_bottom(x_out, y):
    """Bottom of a console side wall whose outer face is at x_out: just into the carpet so no floor shows through, but
    beside the seat cushions it stops just above the cushion's bolster (layout.seat_zone)."""
    # (behind the cushions the bands stay at rim height: the seat backs come in there)
    w = L.seat_zone(y) if y > 0.0 else 1.0
    return (_floor_z(x_out, y) - 0.008) * (1 - w) + L.SEAT_BAND_Z * w


def _sm(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def _band_centre_upright(z, ha):
    e = _stack_edge(z)
    return e + WING_DIR * (_wing_width(z) + ha - 0.005)


# passenger band x on the console: the same as at the stack's foot, so the band runs on in one line (B38 / owner photo)
CON_X = L.CONSOLE_HALF_W_PASS + 0.002     # band centre on the console: inner face 10 mm inside the console's edge


def _band_path(side=1):
    """Smooth centre line of the band (passenger, side=1) or of the driver console bolster (side=-1)."""
    if side > 0:
        ha_top = BAND_UP[0] * 0.80
        top = _band_centre_upright(0.852, ha_top)
        ctrl = [top + Vector((0, 0.070, 0.006)), top + Vector((0, 0.034, 0.012)), top + Vector((0, 0.008, 0.006))]
        for z in (0.835, 0.80, 0.76, 0.72, 0.68, 0.645, BEND_Z0):
            ctrl.append(_band_centre_upright(z, BAND_UP[0]))
        p0 = ctrl[-1]
        t0 = (ctrl[-1] - ctrl[-2]).normalized()
        # one smooth sweep from the stack edge onto the console edge, in the same vertical plane (no swerve)
        p3 = Vector((CON_X, p0.y - 0.120, CON_Z))
        p1 = p0 + t0 * 0.040
        p2 = p3 + Vector((0, 0.065, 0))
        for k in range(1, 9):
            u = k / 9
            ctrl.append(p0 * (1 - u) ** 3 + p1 * 3 * u * (1 - u) ** 2 + p2 * 3 * u * u * (1 - u) + p3 * u ** 3)
        ctrl.append(p3)
        # along the console edge, curving in with it where it narrows between the seat backs (layout.console_half_w)
        for y in (p3.y - 0.10, 0.12, 0.03, -0.06, -0.14, -0.22, -0.30, -0.38, -0.44, -0.497):
            ctrl.append(Vector((L.console_half_w(y)[1] + 0.002, y, CON_Z)))
    else:
        # runs forward under the stack to the dash lower so no end face shows beside the footwell
        ctrl = [Vector((-(L.console_half_w(y)[0] + 0.002), y, CON_Z)) for y in (0.900, 0.75, 0.60, 0.46, 0.34, 0.22, 0.10, -0.06, -0.14, -0.22, -0.30, -0.38, -0.44, -0.497)]
    path = lib.spline_through(ctrl, n_per_seg=6, tension=0.5)
    length = sum((path[i + 1] - path[i]).length for i in range(len(path) - 1))
    return lib.resample_open(path, max(12, int(length / 0.006)))


def _band_rings(path, side=1):
    rings = []
    n = len(path)
    # the section only grows into the tall console wall once the path has finished bending (growing it inside the
    # bend folds the inner side over itself); the lower wall fills the space under the bend
    i3 = next((k for k, p in enumerate(path) if p.z <= CON_Z + 0.0015), 0) if side > 0 else 0
    along = [0.0]
    for k in range(1, n):
        along.append(along[-1] + (path[k] - path[k - 1]).length)
    for i, c in enumerate(path):
        t = (path[min(n - 1, i + 1)] - path[max(0, i - 1)]).normalized()
        s = _sm(BEND_Z0, BEND_Z1, c.z) if side > 0 else 1.0
        up_axis = Vector((side * WING_DIR.x, WING_DIR.y, 0)) if side > 0 else Vector((0, 0, 1))
        a = (up_axis * (1 - s) + Vector((0, 0, 1)) * s)
        a = (a - t * a.dot(t)).normalized()
        b = t.cross(a).normalized()
        if side < 0:
            b = -b          # keep the flatter face toward the cabin centre on the driver side too
        a = b.cross(t).normalized() if side > 0 else t.cross(b).normalized()
        g = _sm(0.0, 0.09, along[i] - along[i3]) if (side > 0 and i >= i3) else (0.0 if side > 0 else 1.0)
        # constant height under the armrest, whose sides come down over it there (console._build_armrest)
        bottom = _wall_bottom(c.x + side * BAND_CON[1], c.y)
        ha_con = (CON_Z + CON_TOP - bottom) / 2 if g > 0 else BAND_CON[0]
        ha = BAND_UP[0] * (1 - g) + ha_con * g
        hb = BAND_UP[1] * (1 - g) + BAND_CON[1] * g
        if side > 0 and c.z > 0.83:
            ha *= 0.80 + 0.20 * _sm(0.865, 0.83, c.z)
        # the console section is a tall padded side wall: its top sits CON_TOP above the centre line and it runs down
        # the console side (offset along a), so the wrap colour covers the console sides as in B38
        top = BAND_UP[0] * (1 - g) + CON_TOP * g
        prof = lib.rounded_rect2d(2 * ha, 2 * hb, min(hb * 0.85, ha), n_corner=6, offset=(top - ha, 0.0))
        rings.append([c + a * q.x + b * q.y for q in prof])
    return rings


def build_grab_handle():
    """Brushed grab wing with its teardrop slot, the wide leather band on its outer edge running into the console,
    and the matching driver-side console bolster (B13 / B21 / B37 / B16 / B38)."""
    for side, cid in ((1, 'dash.grab'), (-1, 'console.bolster.driver')):
        path = _band_path(side)
        rings = _band_rings(path, side)
        # the driver bolster's frame is mirrored, so its winding is reversed to keep the normals pointing out
        band = lib.loft_object(cid, rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=3.0, flip=side < 0)
        lib.add_subsurf(band, 1)
        lib.tag(band, cid, 'dashboard' if side > 0 else 'console')
    # passenger console side under the stack: the dark lower side of the console below the band, running forward to
    # the toe board. Under the stack it steps in to the stack's side so no ledge shows; at the rear it runs on inside
    # the band's console wall so no end face shows.
    band = _band_path(1)
    y_bend0 = next(p.y for p in band if p.z <= BEND_Z0)          # band leaves the stack edge
    y_bend1 = next(p.y for p in band if p.z <= CON_Z + 0.0015)   # band reaches the console line
    hb = BAND_CON[1] - 0.002         # 2 mm inside the band's (subdivided) console wall
    x_stack = STACK_CX + stack_half_w(0.56) - hb                 # flush with the stack's side forward of the band
    rings = []
    for y in [0.900 - 0.64 * k / 40 for k in range(41)]:
        xc = CON_X + (x_stack - CON_X) * _sm(y_bend0, y_bend0 + 0.10, y)
        # top inside the band's console wall behind the bend, under the fin's foot from the bend forward;
        # bottom just into the carpet, which climbs the toe board here
        z_top = 0.573 - 0.025 * _sm(y_bend1 - 0.01, y_bend1 + 0.02, y)
        z_bot = _wall_bottom(xc + hb, y)
        c = Vector((xc, y, (z_top + z_bot) / 2))
        prof = lib.rounded_rect2d(z_top - z_bot, 2 * hb, BAND_CON[1] * 0.85, n_corner=6)
        rings.append([c + Vector((0, 0, 1)) * q.x + Vector((-1, 0, 0)) * q.y for q in prof])
    low = lib.loft_object('dash.grab.lower', rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=3.0)
    lib.add_subsurf(low, 1)
    lib.tag(low, 'dash.grab.lower', 'console', selectable=False)
    # the fin: ruled surface from the stack edge to just inside the band, following the band down the stack and
    # through its bend, so at the foot it lies on the console top and runs into it (owner photo: one piece)
    rings = []
    for k, c in enumerate(band):
        if c.z > 0.850:
            continue        # the band's curl over the dash lip
        a = _stack_edge(max(c.z, 0.556))
        b = c + (a - c).normalized() * 0.010
        rings.append([a.lerp(b, q / 6) for q in range(7)])
        if c.z <= CON_Z + 0.0015:
            break
    n_pass = Vector((-WING_DIR.y, WING_DIR.x, 0.0))   # the fin's passenger-facing normal
    face_out = -n_pass                                 # the driver-facing side
    wing = lib.loft_object('dash.grab_trim', rings, close_u=False, material='metal_brushed', uv_scale=2.0, flip=_loft_needs_flip(rings, face_out))
    lib.add_solidify(wing, 0.005, offset=0.0)
    # leather back on the passenger side of the fin (wrap colour; shows through the slot as on the car)
    back_off = n_pass * 0.0055
    brings = [[p + back_off for p in r] for r in rings]
    back = lib.loft_object('dash.grab.back', brings, close_u=False, material='leather_black', uv_scale=3.0, flip=not _loft_needs_flip(brings, face_out))
    lib.add_solidify(back, 0.006, offset=0.0)
    # teardrop grab slot through the lower half of the fin, nearer its outer edge
    zc = 0.652
    a = _stack_edge(zc); w = _wing_width(zc)
    c = a + WING_DIR * (w * 0.52)
    up = (_stack_edge(zc + 0.01) - _stack_edge(zc - 0.01)).normalized()
    nrm = WING_DIR.cross(up).normalized()
    # outline listed counter-clockwise (like every other cutter) so the boolean subtracts
    slot = [Vector(p) for p in lib.spline_through([Vector(q) for q in reversed(((0.0, 0.052), (0.007, 0.024), (0.0125, -0.020), (0.0105, -0.040), (0.0, -0.047), (-0.0105, -0.040), (-0.0125, -0.020), (-0.007, 0.024)))], n_per_seg=4, closed=True, tension=0.5)]
    cutter = lib.extrude_profile('dash.grab_slot_cut', slot, c - nrm * 0.03, WING_DIR, up, 0.06)
    lib.add_boolean(wing, cutter)
    lib.add_boolean(back, cutter)
    lib.tag(wing, 'dash.grab_trim', 'dashboard')
    lib.tag(back, 'dash.grab.back', 'dashboard', selectable=False)


def _loft_needs_flip(rings, outward):
    """True when the loft's default winding would face away from `outward` on the first quad."""
    a, b, d = Vector(rings[0][0]), Vector(rings[0][1]), Vector(rings[1][0])
    return (b - a).cross(d - a).dot(Vector(outward)) < 0


def build_trim_band():
    """Mid-dash panels that carry the vents. On the car they are part of the leather dash face: almost flush, no bright
    edges, bounded below by a stitched seam that sweeps up toward the door (IMG_4509 / IMG_4499 / IMG_4491)."""
    specs = (
        (-0.70, -0.605, 'dash.trim.driver', lambda s: 0.665, lambda s: 0.795),
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


# ---------------------------------------------------------------------------
# Passenger dash pad (B37 / B38 / B60 / B66 / B13): one long sculpted pad in the wrap colour from behind the grab
# band to the door. It starts at the crease where the black dash top ends, stands proud with its face tilted up
# toward the occupant, and rolls under at the bottom into a shelf over the dark knee area. Two vents are recessed
# into it: a rounded trapezoid near the stack and a taller rounded square at the door end with the two seat
# switches inside the bottom of its bezel.
# ---------------------------------------------------------------------------
PAD_X0, PAD_X1 = 0.150, 0.692
PAD_ZT, PAD_ZB = 0.836, 0.660        # crease at the dash top / underside of the shelf


def _pad_front(x, z):
    """y of the pad's occupant-facing surface at (x, z) (the face only, between the top roll and the bottom roll)."""
    ys = _surface_point(x, PAD_ZT)
    return ys - 0.014 - (0.815 - z) * 0.20


def _pad_section(x):
    """Closed (y, z) section of the pad at x, starting at the crease and running down the face, under the shelf and
    back up just inside the dash surface. Toward the door end it eases back into the dash."""
    e = 1.0 - smoothstep(PAD_X1 - 0.030, PAD_X1, x)
    ys = _surface_point(x, PAD_ZT)
    yb = _pad_front(x, 0.682)
    front = [(ys, PAD_ZT), (ys - 0.006, 0.832), (ys - 0.011, 0.826)]
    front += [(_pad_front(x, z), z) for z in (0.815, 0.795, 0.775, 0.755, 0.735, 0.715, 0.70, 0.69, 0.682)]
    front += [(yb + 0.0015, 0.675), (yb + 0.006, 0.668), (yb + 0.015, 0.6635), (yb + 0.028, 0.661)]
    pts = []
    for y, z in front:
        s = _surface_point(x, z) - 0.004
        pts.append(Vector((x, s + (y - s) * e, z)))
    # underside forward to the dash face, then back up inside the dash surface
    zb = PAD_ZB + (1 - e) * 0.03
    pts.append(Vector((x, _surface_point(x, zb) + 0.004, zb)))
    for z in (0.685, 0.72, 0.76, 0.80, 0.825):
        pts.append(Vector((x, _surface_point(x, z) + 0.004, z)))
    return pts


def _pad_frame(x, z):
    """(centre, u, v, nrm) on the pad face: u toward the door, v up the face, nrm toward the occupant."""
    c = Vector((x, _pad_front(x, z), z))
    u = Vector((1, 0, 0))
    v = Vector((0, _pad_front(x, z + 0.01) - _pad_front(x, z - 0.01), 0.02)).normalized()
    return c, u, v, u.cross(v).normalized()


def _rounded_poly(corners, r, n=6):
    """Counter-clockwise convex polygon with every corner filleted at radius r (2D Vectors)."""
    m = len(corners)
    out = []
    for i in range(m):
        p, a, b = corners[i], corners[i - 1], corners[(i + 1) % m]
        e1, e2 = (a - p).normalized(), (b - p).normalized()
        th = math.acos(max(-1.0, min(1.0, e1.dot(e2))))
        t = r / math.tan(th / 2)
        bis = (e1 + e2).normalized()
        cen = p + bis * (r / math.sin(th / 2))
        t1, t2 = p + e1 * t, p + e2 * t
        a1 = math.atan2(t1.y - cen.y, t1.x - cen.x)
        a2 = math.atan2(t2.y - cen.y, t2.x - cen.x)
        while a2 < a1:
            a2 += 2 * math.pi
        for k in range(n + 1):
            ang = a1 + (a2 - a1) * k / n
            out.append(Vector((cen.x + r * math.cos(ang), cen.y + r * math.sin(ang))))
    return out


def _offset_poly(corners, d):
    """Convex counter-clockwise polygon moved inward by d (outward when d < 0)."""
    m = len(corners)
    lines = []
    for i in range(m):
        a, b = corners[i], corners[(i + 1) % m]
        t = (b - a).normalized()
        n = Vector((-t.y, t.x))          # inward for a counter-clockwise polygon
        lines.append((a + n * d, t))
    out = []
    for i in range(m):
        (p1, t1), (p2, t2) = lines[i - 1], lines[i]
        den = t1.x * t2.y - t1.y * t2.x
        k = ((p2.x - p1.x) * t2.y - (p2.y - p1.y) * t2.x) / den
        out.append(p1 + t1 * k)
    return out


def _pad_vent(cid, x, z, corners, r, louvre_top, louvre_bot, ring_component, switches=0):
    """Vent recessed into the pad: an opening cut through the pad, a dark lined pocket behind it, horizontal vanes
    and a slider inside, and a chrome bezel standing 1.5 mm proud of the face. Returns the cutter for the pad."""
    c, u, v, nrm = _pad_frame(x, z)
    hole = _rounded_poly(corners, r)
    cutter = lib.extrude_profile(f'{cid}.cut', hole, c - nrm * 0.05, u, v, 0.08)
    # pocket liner: walls 0.5 mm inside the cut, facing the opening, closed by a dark floor 30 mm deep
    liner = _rounded_poly(_offset_poly(corners, 0.0005), max(0.002, r - 0.0005))
    front = [c + u * p.x + v * p.y + nrm * 0.001 for p in liner]
    back = [c + u * p.x + v * p.y - nrm * 0.030 for p in liner]
    walls = lib.loft_object(cid, [front, back], close_u=True, cap_end=True, material='plastic_black', flip=_loft_needs_flip([front, back], c - front[0]))
    lib.tag(walls, cid, 'dashboard')
    # vanes across the louvre band (clipped to the opening's width at their height), slightly tipped down
    def width_at(vv):
        xs = []
        for i in range(len(hole)):
            a, b = hole[i], hole[(i + 1) % len(hole)]
            if (a.y - vv) * (b.y - vv) <= 0 and a.y != b.y:
                xs.append(a.x + (b.x - a.x) * (vv - a.y) / (b.y - a.y))
        return (min(xs), max(xs)) if len(xs) >= 2 else (0.0, 0.0)
    nv = 4
    for j in range(nv):
        vv = louvre_top - (louvre_top - louvre_bot) * (j + 0.5) / nv
        x0, x1 = width_at(vv)
        if x1 - x0 < 0.01:
            continue
        o = c + u * ((x0 + x1) / 2) + v * vv - nrm * 0.007
        vane = lib.extrude_profile(f'{cid}.vane{j}', lib.rounded_rect2d(x1 - x0 - 0.002, 0.0035, 0.0012), o, u, (v * 0.94 + nrm * 0.34).normalized(), 0.0018, material='plastic_black_gloss')
        lib.tag(vane, f'{cid}.vane{j}', 'dashboard', selectable=False)
    vv = (louvre_top + louvre_bot) / 2
    knob = lib.extrude_profile(f'{cid}.knob', lib.rounded_rect2d(0.014, 0.007, 0.002), c + v * vv - nrm * 0.0035, u, v, 0.004, material='plastic_black_gloss')
    lib.tag(knob, f'{cid}.knob', 'dashboard', selectable=False)
    # chrome bezel: 4 mm wide outside the opening, covering the liner's front edge
    outer = _rounded_poly(_offset_poly(corners, -0.004), r + 0.004)
    inner = _rounded_poly(_offset_poly(corners, 0.0012), max(0.002, r - 0.0012))
    ring = lib.extrude_profile(f'{cid}.ring', outer, c - nrm * 0.004, u, v, 0.0055, material='metal_brushed')
    ring_cut = lib.extrude_profile(f'{cid}.ring_cut', inner, c - nrm * 0.03, u, v, 0.06)
    lib.add_boolean(ring, ring_cut)
    lib.tag(ring, ring_component, 'trim', selectable=False)
    # seat heat / vent switches in the lower part of the opening, on a dark plate across it
    if switches:
        x0, x1 = width_at(louvre_bot - 0.020)
        plate = lib.extrude_profile(f'{cid}.switch_plate', lib.rounded_rect2d(x1 - x0 + 0.004, 0.026, 0.003), c + u * ((x0 + x1) / 2) + v * (louvre_bot - 0.020) - nrm * 0.006, u, v, 0.005, material='plastic_black')
        lib.tag(plate, f'{cid}.switch_plate', 'dashboard', selectable=False)
        for k in range(switches):
            o = c + u * ((x0 + x1) / 2 + (k - (switches - 1) / 2) * 0.026) + v * (louvre_bot - 0.020) - nrm * 0.0015
            b = lib.extrude_profile(f'dash.passenger_switch_{k}', lib.rounded_rect2d(0.020, 0.016, 0.003), o, u, v, 0.003, material='plastic_black_gloss', bevel=0.0008)
            lib.tag(b, f'dash.passenger_switch.{k}', 'dashboard', selectable=False)
            # light seat icon / indicator on the key top
            mark = lib.extrude_profile(f'dash.passenger_switch_mark_{k}', lib.rounded_rect2d(0.007, 0.006, 0.0015), o + v * 0.001 + nrm * 0.0028, u, v, 0.0006, material='stitch_grey')
            lib.tag(mark, f'dash.passenger_switch.mark{k}', 'dashboard', selectable=False)
    return cutter


def build_passenger_pad():
    n = 64
    rings = [_pad_section(PAD_X0 + (PAD_X1 - PAD_X0) * k / (n - 1)) for k in range(n)]
    pad = lib.loft_object('dash.trim.passenger', rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=2.0, flip=_loft_needs_flip(rings, (0, -0.6, 0.8)))
    # inner vent: a rounded trapezoid whose stack-side edge leans toward the door at the top (B37 / B66 / B58)
    V = lambda pts: [Vector(p) for p in pts]
    inner = V([(-0.050, -0.030), (0.046, -0.030), (0.046, 0.030), (-0.030, 0.030)])
    cut1 = _pad_vent('dash.vents.passenger_inner', 0.305, 0.770, inner, 0.012, 0.024, -0.024, 'dash.vents.passenger_inner.ring')
    # outer vent: taller rounded square at the door end; louvres in the top, the two seat switches below (B66 / B37)
    outer = V([(-0.039, -0.052), (0.039, -0.052), (0.039, 0.052), (-0.039, 0.052)])
    cut2 = _pad_vent('dash.vents.passenger', 0.604, 0.752, outer, 0.013, 0.044, -0.010, 'dash.vents.passenger.ring', switches=2)
    lib.add_boolean(pad, cut1)
    lib.add_boolean(pad, cut2)
    lib.tag(pad, 'dash.trim.passenger', 'trim')


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
    """Rolled, stitched brow of the cockpit wrap: from the driver door along the instrument hood's rear edge, across
    the dash lip above the centre stack, into the top of the passenger band (B13 / B38 / B37). Flat-faced (about
    22 mm tall, 14 mm deep) rather than a thin cord."""
    path = []
    n = 22
    for i in range(n):
        x = -0.69 + (STACK_X0 + 0.02 + 0.69) * i / (n - 1)
        prof = lib.spline_through(profile_at(x), n_per_seg=3)
        rear = [p for p in prof if 0.55 < p.x < 0.70]
        pt = max(rear, key=lambda p: p.y) if rear else prof[5]
        path.append(Vector((x, pt.x - 0.002, pt.y - 0.003)))
    # across the stack it runs along the top edge of the (yawed) stack face, just above the top opening (B58 / B21)
    for x in (-0.095, -0.05, 0.0, 0.05, 0.095):
        path.append(Vector((x, stack_y(x, 0.852) - 0.001, 0.862)))
    band_top = _band_path(1)[6]
    path.append(band_top)
    path = lib.spline_through(path, n_per_seg=3, tension=0.5)
    path = lib.resample_open(path, int(sum((path[i + 1] - path[i]).length for i in range(len(path) - 1)) / 0.006))
    prof = lib.rounded_rect2d(0.022, 0.014, 0.0065, n_corner=5)
    welt = lib.sweep_profile('dash.welt', path, prof, material='leather_black', up_hint=Vector((0, 0, 1)), uv_scale=6.0)
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
    build_passenger_pad()
    build_glovebox_and_switches()
