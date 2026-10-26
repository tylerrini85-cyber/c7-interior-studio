"""Dashboard: upper pad with driver instrument hood, centre stack, passenger side, outer vents, cluster, column shroud,
passenger grab handle, trim band, glovebox, switch panels, defroster strip."""
import math
from mathutils import Vector
import lib
import layout as L

# profile templates: 13 control points (y, z) from cowl to under-dash bottom edge
T_DRIVER_OUTER = [(1.08, 0.82), (0.96, 0.845), (0.84, 0.86), (0.72, 0.865), (0.64, 0.86), (0.60, 0.83), (0.60, 0.78), (0.63, 0.72), (0.66, 0.66), (0.69, 0.60), (0.72, 0.54), (0.76, 0.46), (0.82, 0.41)]
T_HOOD = [(1.08, 0.82), (0.96, 0.855), (0.84, 0.895), (0.72, 0.915), (0.63, 0.915), (0.585, 0.895), (0.60, 0.86), (0.73, 0.85), (0.82, 0.76), (0.80, 0.66), (0.72, 0.56), (0.75, 0.46), (0.82, 0.41)]
T_STACK = [(1.08, 0.82), (0.96, 0.845), (0.84, 0.86), (0.72, 0.865), (0.66, 0.86), (0.635, 0.845), (0.625, 0.82), (0.585, 0.76), (0.54, 0.70), (0.50, 0.64), (0.47, 0.60), (0.44, 0.56), (0.40, 0.50)]
T_PASS = [(1.08, 0.82), (0.96, 0.845), (0.84, 0.86), (0.72, 0.865), (0.64, 0.86), (0.615, 0.835), (0.61, 0.79), (0.625, 0.73), (0.64, 0.68), (0.66, 0.60), (0.69, 0.52), (0.74, 0.45), (0.82, 0.41)]

STACK_X0, STACK_X1 = -0.175, 0.215


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


def build_center_stack():
    yaw = L.STACK_YAW
    rot = lambda p: Vector((p.x * math.cos(yaw) - p.y * math.sin(yaw), p.x * math.sin(yaw) + p.y * math.cos(yaw), p.z))
    # face plane: from top (y=0.63,z=0.83) to bottom (y=0.45,z=0.57) ; width 0.37 centred x=0.02
    top = Vector((0.0, 0.63, 0.83)); bot = Vector((0.0, 0.45, 0.57))
    down = (bot - top).normalized()
    u = Vector((1, 0, 0))
    v = -down
    nrm = u.cross(v)
    cx = 0.02
    # stack plate
    plate_prof = lib.rounded_rect2d(0.31, (bot - top).length + 0.02, 0.02)
    center = (top + bot) / 2 + u * cx
    plate = lib.extrude_profile('console.stack', plate_prof, center, u, v, -0.03, material='plastic_black_gloss', bevel=0.004)
    plate.rotation_euler = (0, 0, yaw)
    lib.tag(plate, 'console.stack', 'console')
    # 8-inch infotainment screen (0.19 x 0.115 active) bezel + glass
    scr_c = top + down * 0.085 + u * cx
    bez = lib.extrude_profile('console.screen_bezel', lib.rounded_rect2d(0.235, 0.15, 0.012), scr_c, u, v, 0.012, material='plastic_black')
    bez.rotation_euler = (0, 0, yaw)
    lib.tag(bez, 'console.screen_bezel', 'console')
    scr = lib.extrude_profile('console.screen', lib.rounded_rect2d(0.19, 0.115, 0.003), scr_c + nrm * 0.0125, u, v, 0.001, material='screen_off')
    scr.rotation_euler = (0, 0, yaw)
    lib.tag(scr, 'console.screen', 'electronics')
    # HVAC panel below the screen: two knobs + button rows
    hv_c = top + down * 0.215 + u * cx
    hv = lib.extrude_profile('console.hvac', lib.rounded_rect2d(0.28, 0.085, 0.01), hv_c, u, v, 0.006, material='plastic_black')
    hv.rotation_euler = (0, 0, yaw)
    lib.tag(hv, 'console.hvac', 'console')
    for k, dx in enumerate((-0.11, 0.11)):
        kn = lib.revolve(f'console.hvac_knob_{k}', [(0, 0), (0.021, 0), (0.021, 0.012), (0.019, 0.014), (0.0, 0.014)], segments=28, material='metal_satin_dark', origin=hv_c + u * dx + nrm * 0.006, direction=nrm)
        kn.rotation_euler = (kn.rotation_euler.x, kn.rotation_euler.y, kn.rotation_euler.z)
        lib.tag(kn, f'console.hvac_knob.{"left" if k == 0 else "right"}', 'console', selectable=False)
    for r in range(2):
        for c in range(4):
            bx = -0.045 + 0.03 * c
            bz = 0.018 - 0.036 * r
            b = lib.extrude_profile(f'console.hvac_btn_{r}{c}', lib.rounded_rect2d(0.024, 0.016, 0.003), hv_c + u * bx + v * bz + nrm * 0.006, u, v, 0.003, material='plastic_black')
            b.rotation_euler = (0, 0, yaw)
            lib.tag(b, f'console.hvac_btn.{r}{c}', 'console', selectable=False)
    # upper vents (two) with the hazard switch between, just under the dash top edge
    vent_c = top + down * -0.0 + u * cx
    for k, dx in enumerate((-0.125, 0.125)):
        frame = lib.extrude_profile(f'dash.vent_center_{k}', lib.rounded_rect2d(0.095, 0.045, 0.008), vent_c + u * dx + down * 0.0 - v * 0.0, u, v, -0.03, material='plastic_black')
        frame.rotation_euler = (0, 0, yaw)
        lib.tag(frame, f'dash.vents.center.{"left" if k == 0 else "right"}', 'dashboard')
        for j in range(3):
            vane = lib.extrude_profile(f'dash.vent_center_{k}_vane{j}', lib.rounded_rect2d(0.085, 0.006, 0.002), vent_c + u * dx + v * (0.013 - 0.013 * j) + nrm * 0.004, u, v, -0.012, material='plastic_black_gloss')
            vane.rotation_euler = (0, 0, yaw)
            lib.tag(vane, f'dash.vents.center.{k}.vane{j}', 'dashboard', selectable=False)
    hz = lib.revolve('dash.hazard', [(0, 0), (0.011, 0), (0.011, 0.004), (0.009, 0.006), (0, 0.006)], segments=24, material='emblem', origin=vent_c, direction=nrm)
    lib.tag(hz, 'dash.hazard', 'dashboard', selectable=False)
    # engine start button on the driver side of the stack, right of the wheel
    sb = lib.revolve('dash.start_button', [(0, 0), (0.016, 0), (0.016, 0.005), (0.013, 0.007), (0, 0.007)], segments=28, material='metal_satin_dark', origin=top + down * 0.16 + u * (cx - 0.165), direction=nrm)
    lib.tag(sb, 'dash.start_button', 'dashboard', selectable=False)


def _surface_point(x, z):
    """(y) of the dash surface at lateral x for height z on the rear (occupant) face."""
    prof = lib.spline_through(profile_at(x), n_per_seg=3)
    cand = min([p for p in prof if p.x < 0.75], key=lambda p: abs(p.y - z))
    return cand.x


def _vent(cid, x, z, w=0.068, h=0.110):
    """Tall rectangular C7 vent with a bright bezel and three horizontal vanes, recessed into the dash."""
    y = _surface_point(x, z)
    c = Vector((x, y, z))
    ang = math.radians(-14 * (1 if x > 0 else -1)) if abs(x) > 0.5 else 0.0
    u = Vector((math.cos(ang), math.sin(ang), 0))
    v = Vector((0, 0.2, 1)).normalized()
    nrm = u.cross(v)
    cavity = lib.extrude_profile(cid, lib.rounded_rect2d(w - 0.012, h - 0.012, 0.008), c - nrm * 0.004, u, v, -0.05, material='plastic_black')
    lib.tag(cavity, cid, 'dashboard')
    for j in range(3):
        vane = lib.extrude_profile(f'{cid}.vane{j}', lib.rounded_rect2d(w - 0.018, 0.005, 0.002), c + v * (0.028 - 0.028 * j) - nrm * 0.010, u, v, -0.012, material='plastic_black_gloss')
        lib.tag(vane, f'{cid}.vane{j}', 'dashboard', selectable=False)
    knob = lib.box(f'{cid}.knob', (0.018, 0.006, 0.008), c - nrm * 0.006, material='plastic_black_gloss')
    lib.tag(knob, f'{cid}.knob', 'dashboard', selectable=False)
    ring = lib.extrude_profile(f'{cid}.ring', lib.rounded_rect2d(w, h, 0.012), c - nrm * 0.006, u, v, 0.008, material='metal_brushed', bevel=0.002)
    hole = lib.extrude_profile(f'{cid}.hole', lib.rounded_rect2d(w - 0.012, h - 0.012, 0.008), c - nrm * 0.03, u, v, 0.06)
    lib.add_boolean(ring, hole)
    lib.tag(ring, f'{cid}.ring', 'trim', selectable=False)


def build_outer_vents():
    _vent('dash.vents.driver', -0.63, 0.735)
    _vent('dash.vents.passenger', 0.655, 0.735)
    _vent('dash.vents.passenger_inner', 0.305, 0.735)
    # passenger seat-heat switch panel beside the outer vent (IMG_4491 / IMG_4509)
    y = _surface_point(0.56, 0.72)
    sw = lib.extrude_profile('dash.passenger_switches', lib.rounded_rect2d(0.034, 0.05, 0.006), (0.56, y - 0.004, 0.715), (1, 0, 0), (0, 0.2, 1), 0.006, material='plastic_black', bevel=0.002)
    lib.tag(sw, 'dash.passenger_switches', 'dashboard', selectable=False)


def build_grab_handle():
    """Passenger grab bar: a wide sculpted aluminium fin running from the dash top down the passenger side of the
    centre stack into the console, with a leather pad along its top edge (IMG_4499 / IMG_4513 / IMG_4494)."""
    x = 0.215
    # outline in the YZ plane following the stack slope; two parallel edges 0.075 apart
    inner = [(0.665, 0.845), (0.60, 0.78), (0.52, 0.70), (0.44, 0.63), (0.36, 0.585), (0.30, 0.57)]
    outer = [(0.36 - 0.06, 0.535), (0.42 - 0.03, 0.57), (0.50 - 0.02, 0.62), (0.58 - 0.02, 0.69), (0.66 - 0.03, 0.765), (0.72, 0.83)]
    pts = [Vector(p) for p in inner] + [Vector(p) for p in outer]
    fin = lib.extrude_profile('dash.grab', pts, (x, 0, 0), (0, 1, 0), (0, 0, 1), 0.024, material='metal_brushed', bevel=0.004)
    lib.tag(fin, 'dash.grab', 'dashboard')
    # leather pad on the top edge
    path = [Vector((x + 0.012, y, z + 0.006)) for (y, z) in inner]
    path = lib.spline_through(path, n_per_seg=3)
    pad = lib.sweep_tube('dash.grab_trim', path, (0.020, 0.012), n=12, cap=True, material='leather_black', up_hint=Vector((1, 0, 0)), uv_scale=3.0)
    lib.tag(pad, 'dash.grab_trim', 'dashboard')


def build_trim_band():
    """Mid-dash trim panels: a tall (~11 cm) sculpted band that carries the vents, on both sides of the cockpit
    (IMG_4491: passenger panel from the stack to the door; IMG_4496/4515: driver panel from the door to the hood)."""
    for (x0, x1, cid) in ((0.245, 0.735, 'dash.trim.passenger'), (-0.735, -0.555, 'dash.trim.driver')):
        n = 18
        xs = [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]
        rings = []
        for z in (0.665, 0.69, 0.72, 0.75, 0.78, 0.795):
            ring = []
            for x in xs:
                # the band bows outward slightly at mid height
                bulge = 0.012 * math.sin(math.pi * (z - 0.665) / 0.13)
                ring.append(Vector((x, _surface_point(x, z) - 0.004 - bulge, z)))
            rings.append(ring)
        band = lib.loft_object(cid, rings, close_u=False, material='leather_black', uv_scale=1.5, flip=True)
        lib.add_solidify(band, 0.006, offset=1.0)
        lib.tag(band, cid, 'trim')
        # bright edge lines along the top and bottom of the panel
        for z in (0.665, 0.795):
            path = [Vector((x, _surface_point(x, z) - 0.006, z)) for x in xs]
            edge = lib.sweep_tube(f'{cid}.edge{int(z * 1000)}', path, 0.003, n=8, cap=True, material='metal_brushed', up_hint=Vector((0, 0, 1)))
            lib.tag(edge, f'{cid}.edge{int(z * 1000)}', 'trim', selectable=False)


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
    # down the driver side of the stack
    for (y, z) in ((0.63, 0.83), (0.58, 0.76), (0.52, 0.69), (0.47, 0.62), (0.44, 0.575)):
        path.append(Vector((STACK_X0 - 0.012, y - 0.01, z)))
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
