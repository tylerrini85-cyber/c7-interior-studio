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
    """Return 2D point (in wheel plane) of the rim centreline at angle a (0 = right/3 o'clock, CCW)."""
    r = R_CENTER
    x, y = r * math.cos(a), r * math.sin(a)
    if variant == 'factory':
        # gentle flattening of the very bottom (C7 wheel has a shallow flat segment under the lower spoke)
        flat = -0.93 * r
        if y < flat:
            y = flat
    elif variant == 'flat_bottom':
        flat = -0.76 * r
        if y < flat:
            y = flat
    elif variant in ('d_shape', 'led_performance'):
        if y < -0.72 * r:
            y = -0.72 * r
        if y > 0.86 * r:
            y = 0.86 * r
    return Vector((x, y))


def rim_radius(variant, a):
    base = L.RIM_RADIUS
    if variant in ('flat_bottom', 'd_shape', 'led_performance'):
        base = 0.019
    # thumb rests: thicker just above the horizontal spokes (10 and 2 o'clock)
    for ta in (math.radians(160), math.radians(20)):
        d = abs((a - ta + math.pi) % (2 * math.pi) - math.pi)
        base += 0.004 * max(0.0, 1 - d / math.radians(22))
    return base


def build_rim_segment(cid, variant, a0, a1, material, c, u, v, n, steps=28):
    path, radii = [], []
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        p2 = rim_centerline(variant, a)
        path.append(c + u * p2.x + v * p2.y)
        radii.append(rim_radius(variant, a))
    obj = lib.sweep_tube(cid, path, 0.0, n=18, radius_fn=lambda t: (radii[min(int(round(t * steps)), steps)], radii[min(int(round(t * steps)), steps)] * 0.92), cap=True, material=material, up_hint=n, uv_scale=4.0)
    lib.tag(obj, cid, 'steering')
    return obj


def build_spokes_and_hub(variant, c, u, v, n):
    thin = variant in ('d_shape', 'led_performance')
    spoke_mat = 'metal_satin_dark' if not thin else 'carbon'
    # horizontal spokes: from hub edge to the rim at 0 and 180 deg, tall flat sections with leather-topped button pods
    for side, cid in ((-1, 'steering.spoke.left'), (1, 'steering.spoke.right')):
        rings = []
        for s, (h, d) in ((0.0, (0.075, 0.026)), (0.55, (0.060, 0.022)), (1.0, (0.042, 0.020))):
            x = side * (0.06 + (R_CENTER - 0.06 + 0.012) * s)
            prof = lib.rounded_rect2d(d, h, 0.012)
            # profile plane: d along n (depth), h along v
            rings.append(lib.place_profile(prof, c + u * x + v * (0.004 - 0.004 * s), n, v))
        sp = lib.loft_object(cid, rings, close_u=True, cap_start=True, cap_end=True, material=spoke_mat)
        lib.add_bevel(sp, 0.004, 3)
        lib.tag(sp, cid, 'steering')
        # switch pod on the front face of the spoke
        pod = lib.extrude_profile(cid + '.pod', lib.rounded_rect2d(0.042, 0.055, 0.008), c + u * (side * 0.088) - n * 0.0, u, v, -0.022, material='plastic_black', bevel=0.003)
        lib.tag(pod, cid + '.pod', 'steering', selectable=False)
        for r in range(2):
            for k in range(2):
                b = lib.extrude_profile(f'{cid}.btn{r}{k}', lib.rounded_rect2d(0.016, 0.014, 0.003), c + u * (side * 0.088 + (k - 0.5) * 0.019) + v * (0.014 - 0.028 * r) - n * 0.023, u, v, -0.003, material='plastic_black_gloss')
                lib.tag(b, f'{cid}.btn{r}{k}', 'steering', selectable=False)
        # paddle shifter behind the spoke (A8)
        pad = lib.extrude_profile(cid + '.paddle', lib.rounded_rect2d(0.075, 0.045, 0.012), c + u * (side * 0.125) + v * 0.0 + n * 0.035, u, v, 0.004, material='metal_satin_dark', bevel=0.002)
        lib.tag(pad, 'steering.paddle.left' if side < 0 else 'steering.paddle.right', 'steering', selectable=False)
    # lower spoke: broad tapering blade from hub to rim bottom
    rings = []
    bottom = rim_centerline(variant, -math.pi / 2).y
    for s, (w, d) in ((0.0, (0.075, 0.03)), (0.6, (0.055, 0.022)), (1.0, (0.045, 0.02))):
        y = -0.045 + (bottom + 0.012 + 0.045) * s
        prof = lib.rounded_rect2d(w, d, 0.008)
        rings.append(lib.place_profile(prof, c + v * y, u, n))
    low = lib.loft_object('steering.spoke.lower', rings, close_u=True, cap_start=True, cap_end=True, material=spoke_mat)
    lib.add_bevel(low, 0.003, 3)
    lib.tag(low, 'steering.spoke.lower', 'steering')
    # lower spoke trim insert (brushed)
    ins = lib.extrude_profile('steering.spoke.lower.insert', lib.rounded_rect2d(0.03, 0.07, 0.006), c + v * (-0.085) - n * 0.012, u, v, -0.002, material='metal_brushed')
    lib.tag(ins, 'steering.spoke.lower.insert', 'steering', selectable=False)
    # hub / airbag cover: shield-shaped (wider at top), domed toward the driver
    shield = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        t = 0.5 + 0.5 * math.sin(a)          # 1 at top, 0 at bottom (smooth)
        rx = 0.062 + 0.011 * t
        ry = 0.055 - 0.004 * t
        shield.append(Vector((rx * math.cos(a), ry * math.sin(a))))
    rings = []
    for scale, depth in ((0.94, 0.030), (1.0, 0.010), (1.0, -0.016), (0.975, -0.024), (0.90, -0.029), (0.70, -0.032), (0.40, -0.0335)):
        rings.append(lib.place_profile(shield, c - n * depth, u, v, scale=(scale, scale)))
    hub = lib.loft_object('steering.hub', rings, close_u=True, cap_start=True, cap_end=True, material='plastic_soft')
    lib.tag(hub, 'steering.hub', 'steering')
    # emblem placeholder (development stand-in for the crossed flags): a bevelled badge with 'C7' text
    badge = lib.extrude_profile('steering.emblem', lib.rounded_rect2d(0.034, 0.024, 0.006), c - n * 0.034, u, v, -0.003, material='chrome', bevel=0.001)
    lib.tag(badge, 'steering.emblem', 'steering')
    txt = lib.text_object('steering.emblem.text', 'C7', 0.012, c - n * 0.0375, u, v, extrude=0.0005, material='emblem')
    lib.tag(txt, 'steering.emblem.text', 'steering', selectable=False)
    # centre marker stripe for performance wheels at 12 o'clock
    if thin:
        top = rim_centerline(variant, math.pi / 2).y
        stripe = lib.extrude_profile('steering.rim.marker', lib.rounded_rect2d(0.02, 0.012, 0.003), c + v * (top) - n * (rim_radius(variant, math.pi / 2) - 0.002), u, v, -0.003, material='emblem')
        lib.tag(stripe, 'steering.rim.marker', 'steering', selectable=False)
    if variant == 'led_performance':
        top = rim_centerline(variant, math.pi / 2).y
        for k in range(11):
            x = -0.05 + 0.01 * k
            led = lib.extrude_profile(f'steering.led_{k}', lib.rounded_rect2d(0.006, 0.004, 0.001), c + u * x + v * (top - 0.036) - n * 0.001, u, v, -0.002, material='emissive_white')
            lib.tag(led, f'steering.led.{k}', 'steering', selectable=False)
        strip = lib.extrude_profile('steering.led_strip', lib.rounded_rect2d(0.125, 0.012, 0.004), c + v * (top - 0.036) + n * 0.0, u, v, 0.006, material='plastic_black_gloss')
        lib.tag(strip, 'steering.led_strip', 'steering', selectable=False)


def build(variant='factory', center=None):
    c, u, v, n = wheel_frame(center)
    d = math.radians
    rim_mat = 'leather_black'
    build_rim_segment('steering.rim.upper', variant, d(28), d(152), rim_mat, c, u, v, n)
    build_rim_segment('steering.grip.left', variant, d(150), d(212), rim_mat, c, u, v, n)
    build_rim_segment('steering.rim.lower', variant, d(210), d(332), rim_mat, c, u, v, n)
    build_rim_segment('steering.grip.right', variant, d(330), d(392), rim_mat, c, u, v, n)
    build_spokes_and_hub(variant, c, u, v, n)
