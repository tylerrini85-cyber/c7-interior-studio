"""Steering wheels. Factory C7 three-spoke 14.1 in wheel plus geometry variants (flat bottom, D-shape performance, LED)."""
import math
from mathutils import Vector
import lib
import layout as L

R_CENTER = L.WHEEL_RADIUS - L.RIM_RADIUS   # rim centreline radius

VARIANTS = ['factory', 'flat_bottom', 'd_shape', 'led_performance']


def wheel_frame(center=None, tilt=None):
    c = Vector(center or L.WHEEL_CENTER)
    t = L.WHEEL_TILT if tilt is None else tilt
    u = Vector((1, 0, 0))
    v = Vector((0, math.sin(t), math.cos(t)))      # up in the wheel plane
    n = u.cross(v)                                  # toward the driver (-Y) and up
    return c, u, v, n


def rim_centerline(variant, a):
    """2D point (wheel plane) of the rim centreline at angle a (0 = 3 o'clock, CCW). The factory Stingray wheel is
    round (IMG_4493/4499/4511/4516); the flat bottom is the Z06/ZR1-style option (IMG_4495/4514)."""
    r = R_CENTER
    x, y = r * math.cos(a), r * math.sin(a)
    flat = {'factory': -1.01, 'flat_bottom': -0.66, 'd_shape': -0.62, 'led_performance': -0.62}[variant] * r
    if y < flat:
        y = flat
    if variant in ('d_shape', 'led_performance') and y > 0.84 * r:
        y = 0.84 * r
    return Vector((x, y))


def rim_radius(variant, a):
    base = L.RIM_RADIUS if variant == 'factory' else 0.019
    # thumb rests: thicker just above the horizontal spokes (10 and 2 o'clock)
    for ta in (math.radians(155), math.radians(25)):
        d = abs((a - ta + math.pi) % (2 * math.pi) - math.pi)
        base += 0.006 * max(0.0, 1 - d / math.radians(26))
    return base


def build_rim_segment(cid, variant, a0, a1, material, c, u, v, n, steps=28):
    path, radii = [], []
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        p2 = rim_centerline(variant, a)
        path.append(c + u * p2.x + v * p2.y)
        radii.append(rim_radius(variant, a))
    obj = lib.sweep_tube(cid, path, 0.0, n=18, radius_fn=lambda t: (radii[min(int(round(t * steps)), steps)], radii[min(int(round(t * steps)), steps)] * 0.9), cap=True, material=material, up_hint=n, uv_scale=4.0)
    lib.tag(obj, cid, 'steering')
    return obj


def _plate(cid, pts2d, c, u, v, n, depth, back, material, bevel=0.003):
    """Flat plate in the wheel plane: pts2d outline (CCW), extruded from depth `back` toward the driver by `depth`."""
    prof = [Vector(p) for p in pts2d]
    obj = lib.extrude_profile(cid, prof, c - n * back, u, v, depth, material=material, bevel=bevel, bevel_segments=3)
    return obj


# ---------------------------------------------------------------------------
# Wheel centre, measured from the owner photo and B21 / B04 / B17 / B37 (all in the wheel plane, metres from the
# wheel centre, x toward 3 o'clock, y up):
#   airbag  a big shield, flat-topped with rounded corners, tapering to a soft point well below the centre
#   frame   one silver piece: short wide spokes from the rim at 3 and 9 o'clock carrying the switch pods, joined by a
#           slim U that wraps the lower half of the airbag
#   base    a wide black lower spoke from the U down to the rim, with an opening either side of it
# ---------------------------------------------------------------------------
AIRBAG_HALF = [(0.0, 0.056), (0.040, 0.054), (0.062, 0.046), (0.072, 0.028), (0.072, 0.000), (0.066, -0.040),
               (0.052, -0.078), (0.031, -0.104), (0.0, -0.114)]


def _closed_mirror(half):
    """Closed outline from a right-hand half listed top to bottom (x >= 0), counter-clockwise."""
    right = [Vector(p) for p in half]
    left = [Vector((-p[0], p[1])) for p in reversed(half[1:-1])]
    pts = list(reversed(right)) + list(reversed(left))
    return _ccw(pts)


def _ccw(pts):
    area = sum(pts[i].x * pts[(i + 1) % len(pts)].y - pts[(i + 1) % len(pts)].x * pts[i].y for i in range(len(pts)))
    return pts if area > 0 else list(reversed(pts))


def _airbag_outline(grow=0.0):
    pts = lib.spline_through(_closed_mirror(AIRBAG_HALF), n_per_seg=4, closed=True, tension=0.5)
    if grow:
        cen = Vector((0.0, -0.025))
        pts = [cen + (p - cen) * (1 + grow / (p - cen).length) for p in pts]
    return pts


def _frame_outline(variant):
    """Left half of the silver frame (spoke + half of the U), as an outer edge from the bottom centre to the wing's top
    inner corner and an inner edge (hugging the airbag) back down; mirrored into one closed U-with-wings outline."""
    def rim_pt(y):
        x = math.sqrt(max(0.0, R_CENTER ** 2 - y * y))
        return (-(x + 0.004), y)
    # slim U (about 13 mm) under the airbag; wings just big enough to frame the pods with a slim silver border, their
    # top edges running out from the airbag's top corners and rising slightly to the rim
    outer = [(0.0, -0.128), (-0.027, -0.1245), (-0.051, -0.109), (-0.070, -0.083), (-0.081, -0.058), (-0.098, -0.042),
             (-0.126, -0.036), rim_pt(-0.037), rim_pt(-0.010), rim_pt(0.022), rim_pt(0.051), (-0.126, 0.051),
             (-0.098, 0.048), (-0.070, 0.047)]
    inner = [(-0.0715, 0.034), (-0.0735, 0.010), (-0.0705, -0.025), (-0.0605, -0.062), (-0.043, -0.093), (-0.022, -0.110), (0.0, -0.1155)]
    left = outer + inner
    right = [(-x, y) for (x, y) in reversed(left)]
    pts = _ccw([Vector(p) for p in left[:-1] + right[:-1]])
    # smooth it (round U bottom, soft wing corners) without losing the points that sit inside the rim
    return [Vector(p) for p in lib.spline_through(pts, n_per_seg=4, closed=True, tension=0.45)]


def _pod(cid, side, c, u, v, n, front):
    """Black switch pod set into a spoke, with individual keys (left: cruise; right: audio / phone with a 4-way pad)."""
    pc = Vector((side * 0.1115, 0.006))
    # inner edge along the airbag, outer edge along the rim (x > 0 here = toward the rim)
    quad = [Vector((side * x, y)) for x, y in ((-0.024, -0.029), (0.024, -0.025), (0.027, 0.033), (-0.024, 0.029))]
    quad = _ccw([pc + q for q in quad])
    prof = [Vector(p) for p in lib.spline_through(quad, n_per_seg=5, closed=True, tension=0.35)]
    pod = lib.extrude_profile(cid, prof, c + n * (front - 0.004), u, v, 0.0055, material='plastic_black_gloss', bevel=0.0012)
    lib.tag(pod, cid, 'steering', selectable=False)
    top = front + 0.0015
    keys = []
    if side < 0:
        keys = [(-0.010, 0.017, 0.016, 0.010), (0.010, 0.018, 0.016, 0.010), (-0.010, 0.004, 0.016, 0.010), (0.010, 0.005, 0.016, 0.010), (-0.010, -0.009, 0.016, 0.010), (0.010, -0.008, 0.016, 0.010), (0.0, -0.021, 0.034, 0.007)]
    else:
        keys = [(0.013, 0.017, 0.014, 0.010), (0.013, 0.004, 0.014, 0.010), (0.013, -0.009, 0.014, 0.010), (0.0, -0.021, 0.034, 0.007)]
        disc = lib.revolve(cid + '.dpad', [(0, 0), (0.0115, 0), (0.0115, 0.0018), (0.010, 0.0026), (0.0, 0.0026)], segments=28, material='plastic_black', origin=c + u * (pc.x - 0.008) + v * (pc.y + 0.006) + n * top, direction=n)
        lib.tag(disc, cid + '.dpad', 'steering', selectable=False)
    for k, (x, y, w, h) in enumerate(keys):
        o = c + u * (pc.x + side * x) + v * (pc.y + y) + n * top
        key = lib.extrude_profile(f'{cid}.key{k}', lib.rounded_rect2d(w, h, 0.0025), o, u, v, 0.0022, material='plastic_black', bevel=0.0006)
        lib.tag(key, f'{cid}.key{k}', 'steering', selectable=False)


def build_spokes_and_hub(variant, c, u, v, n):
    thin = variant in ('d_shape', 'led_performance')
    frame_mat = 'carbon' if thin else 'metal_brushed'
    bottom = rim_centerline(variant, -math.pi / 2).y
    FRAME_FRONT = 0.012          # frame face, toward the driver from the wheel plane
    # ---- silver frame: one U-with-wings outline (the registry's spoke component)
    outline = _frame_outline(variant)
    frame = lib.extrude_profile('steering.spoke.left', outline, c + n * (FRAME_FRONT - 0.016), u, v, 0.016, material=frame_mat, bevel=0.0025, bevel_segments=3)
    lib.tag(frame, 'steering.spoke.left', 'steering')
    # ---- black lower spoke from the U down into the rim; the gaps beside it are the two lower openings
    base = [Vector(p) for p in ((-0.042, -0.118), (0.042, -0.118), (0.060, bottom + 0.004), (-0.060, bottom + 0.004))]
    lower = lib.extrude_profile('steering.spoke.base', _ccw(base), c + n * (FRAME_FRONT - 0.020), u, v, 0.017, material='leather_black', bevel=0.003, bevel_segments=3)
    lib.tag(lower, 'steering.spoke.base', 'steering')
    # ---- switch pods in the spokes, paddles behind
    for side, cid in ((-1, 'steering.pod.left'), (1, 'steering.pod.right')):
        # (pod nodes are not named after the spokes, so they keep their own black finish)
        _pod(cid, side, c, u, v, n, FRAME_FRONT)
        pad = lib.extrude_profile(cid + '.paddle', lib.rounded_rect2d(0.078, 0.044, 0.012), c + u * (side * 0.128) + v * 0.020 - n * 0.030, u, v, -0.004, material='metal_satin_dark', bevel=0.0015)
        lib.tag(pad, 'steering.paddle.left' if side < 0 else 'steering.paddle.right', 'steering', selectable=False)
    if variant != 'factory':
        flat_trim = lib.extrude_profile('steering.rim.flat_trim', lib.rounded_rect2d(0.11, 0.016, 0.005), c + v * (bottom - 0.004) - n * (L.RIM_RADIUS - 0.004), u, v, -0.004, material=frame_mat)
        lib.tag(flat_trim, 'steering.rim.flat_trim', 'steering', selectable=False)
    # ---- airbag: the shield, domed toward the driver, sitting in the frame
    shield = _airbag_outline()
    rings = []
    for grow, depth in ((-0.004, -0.004), (0.0, 0.004), (0.0, 0.016), (-0.003, 0.024), (-0.010, 0.030), (-0.030, 0.0355), (-0.060, 0.0375)):
        rings.append([c + u * q.x + v * q.y + n * depth for q in _airbag_outline(grow)] if grow else [c + u * q.x + v * q.y + n * depth for q in shield])
    hub = lib.loft_object('steering.hub', rings, close_u=True, cap_start=True, cap_end=True, material='plastic_soft')
    lib.tag(hub, 'steering.hub', 'steering')
    # the crossed-flags emblem is a transparent decal the runtime places on the airbag cover (no carrier plate)
    if thin:
        top = rim_centerline(variant, math.pi / 2).y
        stripe = lib.extrude_profile('steering.rim.marker', lib.rounded_rect2d(0.02, 0.012, 0.003), c + v * top - n * (rim_radius(variant, math.pi / 2) - 0.002), u, v, -0.003, material='emblem')
        lib.tag(stripe, 'steering.rim.marker', 'steering', selectable=False)
    if variant == 'led_performance':
        top = rim_centerline(variant, math.pi / 2).y
        for k in range(11):
            led = lib.extrude_profile(f'steering.led_{k}', lib.rounded_rect2d(0.006, 0.004, 0.001), c + u * (-0.05 + 0.01 * k) + v * (top - 0.036) - n * 0.001, u, v, -0.002, material='emissive_white')
            lib.tag(led, f'steering.led.{k}', 'steering', selectable=False)
        strip = lib.extrude_profile('steering.led_strip', lib.rounded_rect2d(0.125, 0.012, 0.004), c + v * (top - 0.036), u, v, 0.006, material='plastic_black_gloss')
        lib.tag(strip, 'steering.led_strip', 'steering', selectable=False)


def build(variant='factory', center=None):
    c, u, v, n = wheel_frame(center)
    d = math.radians
    rim_mat = 'leather_black'
    build_rim_segment('steering.rim.upper', variant, d(25), d(155), rim_mat, c, u, v, n)
    build_rim_segment('steering.grip.left', variant, d(153), d(217), rim_mat, c, u, v, n)
    build_rim_segment('steering.rim.lower', variant, d(215), d(327), rim_mat, c, u, v, n, steps=48)
    build_rim_segment('steering.grip.right', variant, d(325), d(387), rim_mat, c, u, v, n)
    build_spokes_and_hub(variant, c, u, v, n)
