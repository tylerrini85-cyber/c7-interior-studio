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
        base += 0.0045 * max(0.0, 1 - d / math.radians(24))
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


def build_spokes_and_hub(variant, c, u, v, n):
    thin = variant in ('d_shape', 'led_performance')
    frame_mat = 'carbon' if thin else 'metal_brushed'
    bottom = rim_centerline(variant, -math.pi / 2).y
    # ---- silver Y frame: left arm, right arm, lower stem (one visual piece, three meshes sharing the component)
    # arms rise from the hub to the rim at about 9:30 and 2:30 (IMG_4499/4516); pods sit at their outer ends
    arm_l = [(-0.040, 0.038), (-0.118, 0.052), (-0.150, 0.054), (-0.160, 0.034), (-0.148, 0.004), (-0.118, -0.008), (-0.040, -0.034)]
    arm_r = [(-x, y) for (x, y) in reversed(arm_l)]
    stem = [(-0.032, -0.036), (0.032, -0.036), (0.020, bottom + 0.012), (-0.020, bottom + 0.012)]
    for cid, pts in (('steering.spoke.left', arm_l), ('steering.spoke.right', arm_r), ('steering.spoke.lower', stem)):
        pl = _plate(cid, pts, c, u, v, n, -0.018, 0.0, frame_mat)
        lib.tag(pl, cid, 'steering')
    # ---- black switch pods inset into the outer ends of the arms
    for side, cid in ((-1, 'steering.spoke.left'), (1, 'steering.spoke.right')):
        pc = c + u * (side * 0.120) + v * 0.023
        pod = lib.extrude_profile(cid + '.pod', lib.rounded_rect2d(0.038, 0.050, 0.008), pc - n * 0.001, u, v, -0.006, material='plastic_black')
        lib.tag(pod, cid + '.pod', 'steering', selectable=False)
        for r in range(3):
            b = lib.extrude_profile(f'{cid}.btn{r}', lib.rounded_rect2d(0.026, 0.012, 0.003), pc + v * (0.015 - 0.015 * r) - n * 0.0015, u, v, -0.0025, material='plastic_black_gloss')
            lib.tag(b, f'{cid}.btn{r}', 'steering', selectable=False)
        # paddle shifter behind the rim (A8): thin blade behind the arm, reachable from the rim
        pad = lib.extrude_profile(cid + '.paddle', lib.rounded_rect2d(0.078, 0.044, 0.012), c + u * (side * 0.128) + v * 0.020 - n * 0.030, u, v, -0.004, material='metal_satin_dark', bevel=0.0015)
        lib.tag(pad, 'steering.paddle.left' if side < 0 else 'steering.paddle.right', 'steering', selectable=False)
    # ---- lower insert (badge plate) on the stem, and the flat-bottom trim on the rim
    ins = lib.extrude_profile('steering.spoke.lower.insert', lib.rounded_rect2d(0.030, 0.034, 0.005), c + v * (bottom + 0.045) - n * 0.0045, u, v, 0.002, material='plastic_black_gloss')
    lib.tag(ins, 'steering.spoke.lower.insert', 'steering', selectable=False)
    if variant != 'factory':
        flat_trim = lib.extrude_profile('steering.rim.flat_trim', lib.rounded_rect2d(0.11, 0.016, 0.005), c + v * (bottom - 0.004) - n * (L.RIM_RADIUS - 0.004), u, v, -0.004, material=frame_mat)
        lib.tag(flat_trim, 'steering.rim.flat_trim', 'steering', selectable=False)
    # ---- hub / airbag: shield outline, wide at the top, drawn to a soft point at the bottom
    shield = []
    for i in range(48):
        t = i / 48
        a = 2 * math.pi * t
        # superellipse-ish shield: wider at top, pointed bottom
        rx = 0.066 * (1.0 if math.sin(a) > 0 else 0.88)
        ry = 0.048 if math.sin(a) > 0 else 0.066
        x = rx * math.copysign(abs(math.cos(a)) ** 0.9, math.cos(a))
        y = ry * math.copysign(abs(math.sin(a)) ** (1.0 if math.sin(a) > 0 else 1.25), math.sin(a))
        shield.append(Vector((x, y)))
    rings = []
    for scale, depth in ((0.90, 0.028), (1.0, 0.006), (1.0, -0.016), (0.97, -0.025), (0.88, -0.030), (0.60, -0.0335), (0.25, -0.035)):
        rings.append(lib.place_profile(shield, c - n * depth, u, v, scale=(scale, scale)))
    hub = lib.loft_object('steering.hub', rings, close_u=True, cap_start=True, cap_end=True, material='plastic_soft')
    lib.tag(hub, 'steering.hub', 'steering')
    # emblem carrier: a flat badge the runtime textures with the crossed-flags image supplied by the owner
    badge = lib.extrude_profile('steering.emblem', lib.rounded_rect2d(0.046, 0.024, 0.003), c + v * 0.004 + n * 0.0352, u, v, 0.0015, material='chrome')
    lib.tag(badge, 'steering.emblem', 'steering')
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
