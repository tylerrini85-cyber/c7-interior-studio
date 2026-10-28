"""Centre console (automatic): tunnel console body, shifter plate, A8 shifter with boot, drive-mode dial, EPB switch,
cupholders with sliding cover, armrest lid, side trims. Manual variant swaps the shifter."""
import math
from mathutils import Vector
import lib
import layout as L

SHIFTER_VARIANTS = ['automatic', 'manual', 'short_throw']


def _ss(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def console_half_w(y):
    """(driver, passenger) half widths of the console at station y. Full width at the shifter and the armrest's front;
    behind that it narrows evenly between the seat backs, whose lower bolsters come in to about x 0.15 at y -0.15 and
    0.095 at y -0.35 (it keeps 5-10 mm clear of them, like the armrest between the bolsters in B60 / B38)."""
    t = _ss(0.0, -0.32, y)          # one long, even taper from the armrest's front (no waist)
    return L.CONSOLE_HALF_W + (0.088 - L.CONSOLE_HALF_W) * t, L.CONSOLE_HALF_W_PASS + (0.088 - L.CONSOLE_HALF_W_PASS) * t


def _console_section(y):
    """Closed ring (X-Z) of the console body at station y. The passenger side stays flat right out under the grab
    band (its inner face is at about CONSOLE_HALF_W_PASS - 0.01) so no trench shows beside it."""
    hw, hp = console_half_w(y)
    # top height varies: 0.56 at the shifter area rising to 0.585 under the armrest
    top = L.CONSOLE_TOP_Z + 0.025 * lib.__dict__.get('smooth', lambda a, b, x: max(0, min(1, (x - a) / (b - a))))(0.0, -0.12, y) if False else L.CONSOLE_TOP_Z
    if y < -0.08:
        top = L.CONSOLE_TOP_Z + 0.02 * min(1.0, (-0.08 - y) / 0.08)
    base_z = 0.10
    pts = [
        (-hw - 0.06, base_z), (-hw - 0.02, base_z + 0.02), (-hw, 0.30), (-hw + 0.005, 0.46), (-hw + 0.02, top - 0.02), (-hw + 0.05, top),
        (-hw + 0.10, top + 0.003), (0.0, top + 0.004), (hp - 0.10, top + 0.003), (hp - 0.006, top), (hp - 0.002, top - 0.02),
        (hp, 0.46), (hp, 0.30), (hp + 0.02, base_z + 0.02), (hp + 0.06, base_z), (0.0, base_z - 0.02),
    ]
    return [Vector((x, y, z)) for x, z in pts]


def build_body():
    ys = [0.60, 0.55, 0.50, 0.46, 0.42, 0.36, 0.28, 0.20, 0.12, 0.04, -0.04, -0.07, -0.10, -0.13, -0.16, -0.19, -0.22, -0.25, -0.28, -0.32, -0.38, -0.44, -0.48, -0.50]
    rings = [_console_section(y) for y in ys]
    body = lib.loft_object('console.main', rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=1.5)
    lib.add_subsurf(body, 1)
    lib.tag(body, 'console.main', 'console')
    # brushed plate on the driver half: carries the shifter, the drive-mode dial and the EPB (B37 / B44 / B38)
    plate = lib.extrude_profile('console.trim', lib.rounded_rect2d(0.122, 0.340, 0.018), (-0.052, 0.300, L.CONSOLE_TOP_Z + 0.004), (1, 0, 0), (0, 1, 0), 0.006, material='metal_brushed', bevel=0.002)
    lib.tag(plate, 'console.trim', 'console')
    # small switch square at the front of the passenger half, beside the shifter
    sq = lib.extrude_profile('console.small_switches', lib.rounded_rect2d(0.050, 0.042, 0.006), (0.068, 0.420, L.CONSOLE_TOP_Z + 0.004), (1, 0, 0), (0, 1, 0), 0.006, material='plastic_black_gloss', bevel=0.002)
    lib.tag(sq, 'console.small_switches', 'console', selectable=False)


def build_shifter(variant='automatic'):
    y = L.SHIFTER_Y
    base = Vector((L.SHIFTER_X, y, L.CONSOLE_TOP_Z + 0.01))
    if variant == 'automatic':
        # leather boot: low truncated pyramid with a soft collar (about 95 x 110 mm at the plate, 38 mm tall)
        rings = []
        for s_, (w, d, h) in ((0.0, (0.090, 0.110, 0.0)), (0.5, (0.058, 0.072, 0.022)), (1.0, (0.030, 0.034, 0.038))):
            prof = lib.rounded_rect2d(w, d, 0.010)
            rings.append(lib.place_profile(prof, base + Vector((0, 0, h)), (1, 0, 0), (0, 1, 0)))
        boot = lib.loft_object('console.shifter.boot', rings, close_u=True, cap_start=True, cap_end=False, material='leather_black', uv_scale=3.0)
        lib.add_subsurf(boot, 1)
        lib.tag(boot, 'console.shifter.boot', 'console')
        # short lever leaning slightly rearward, then the leather knob with its chrome collar
        top = base + Vector((0, -0.016, 0.090))
        lever = lib.sweep_tube('console.shifter.lever', [base + Vector((0, 0, 0.030)), top], 0.009, n=16, material='metal_satin_dark')
        lib.tag(lever, 'console.shifter.lever', 'console', selectable=False)
        knob = lib.revolve('console.shifter.knob', [(0.0, 0.0), (0.015, 0.0), (0.019, 0.008), (0.0225, 0.026), (0.0215, 0.046), (0.017, 0.060), (0.009, 0.066), (0.0, 0.067)], segments=32, material='leather_black', origin=top - Vector((0, 0, 0.004)), direction=(0, -0.16, 1))
        lib.tag(knob, 'console.shifter.knob', 'console')
        ring = lib.revolve('console.shifter.ring', [(0.016, 0.0), (0.0205, 0.0), (0.0205, 0.009), (0.016, 0.009)], segments=32, material='chrome', origin=top - Vector((0, 0, 0.006)), direction=(0, -0.16, 1))
        lib.tag(ring, 'console.shifter.ring', 'trim', selectable=False)
        # PRNDL indicator strip beside the boot
        ind = lib.extrude_profile('console.shifter.indicator', lib.rounded_rect2d(0.010, 0.085, 0.003), base + Vector((-0.050, 0.0, 0.0)), (1, 0, 0), (0, 1, 0), 0.001, material='screen_off')
        lib.tag(ind, 'console.shifter.indicator', 'electronics', selectable=False)
    else:
        # manual: round boot and taller lever with a spherical knob
        rings = []
        for s, (r, h) in ((0.0, (0.050, 0.0)), (0.5, (0.030, 0.035)), (1.0, (0.016, 0.065))):
            rings.append(lib.place_profile(lib.circle2d(r, 28), base + Vector((0, 0, h)), (1, 0, 0), (0, 1, 0)))
        boot = lib.loft_object('console.shifter.boot', rings, close_u=True, cap_start=True, cap_end=False, material='leather_black', uv_scale=3.0)
        lib.add_subsurf(boot, 1)
        lib.tag(boot, 'console.shifter.boot', 'console')
        h = 0.15 if variant == 'manual' else 0.12
        top = base + Vector((0, -0.015, h))
        lever = lib.sweep_tube('console.shifter.lever', [base + Vector((0, 0, 0.06)), top], 0.010, n=16, material='metal_brushed')
        lib.tag(lever, 'console.shifter.lever', 'console', selectable=False)
        knob = lib.revolve('console.shifter.knob', [(0.0, 0.0), (0.016, 0.0), (0.024, 0.016), (0.022, 0.034), (0.0, 0.042)], segments=32, material='leather_black', origin=top, direction=(0, -0.1, 1), subsurf=1)
        lib.tag(knob, 'console.shifter.knob', 'console')


def build_dial_and_switches():
    # drive-mode selector dial and the EPB switch behind the shifter, side by side on the brushed plate (B37 / B44)
    c = Vector((-0.080, L.DIAL_Y, L.CONSOLE_TOP_Z + 0.010))
    dial = lib.revolve('console.drive_mode_dial', [(0.0, 0.0), (0.026, 0.0), (0.028, 0.014), (0.025, 0.020), (0.011, 0.022), (0.0, 0.022)], segments=36, material='metal_satin_dark', origin=c, direction=(0, 0, 1))
    lib.tag(dial, 'console.drive_mode_dial', 'console')
    base = lib.revolve('console.drive_mode_base', [(0.0, 0.0), (0.034, 0.0), (0.036, 0.004), (0.0, 0.004)], segments=36, material='plastic_black', origin=c - Vector((0, 0, 0.003)), direction=(0, 0, 1))
    lib.tag(base, 'console.drive_mode_base', 'console', selectable=False)
    epb = lib.extrude_profile('console.epb', lib.rounded_rect2d(0.026, 0.040, 0.005), (-0.025, L.DIAL_Y, L.CONSOLE_TOP_Z + 0.010), (1, 0, 0), (0, 1, 0), 0.007, material='plastic_black', bevel=0.002)
    lib.tag(epb, 'console.epb', 'console', selectable=False)


def build_cupholders_and_armrest():
    # long closed storage / cupholder lid on the passenger half, from beside the shifter back to the armrest
    lid = lib.extrude_profile('console.cupholder_plate', lib.rounded_rect2d(0.110, 0.330, 0.016), (0.068, 0.205, L.CONSOLE_TOP_Z + 0.002), (1, 0, 0), (0, 1, 0), 0.006, material='plastic_black_gloss', bevel=0.002)
    lib.tag(lid, 'console.cupholder_plate', 'console')
    _build_armrest()


# armrest (owner photo / B60 / B38): a padded rise out of the console top rather than a slab on it. Its front seam
# slants from just behind the silver plate on the driver side back to behind the storage lid on the passenger side,
# then turns down the passenger edge in a large radius; ahead of the seam the pad sits just under the console top.
ARM_SEAM_D = (-0.155, 0.115)     # seam at the driver edge (x, y)
ARM_SEAM_P = (0.120, 0.025)      # seam where it starts to turn down the passenger side
ARM_CORNER_R = 0.075


def _arm_seam_y(x):
    (x0, y0), (x1, y1) = ARM_SEAM_D, ARM_SEAM_P
    y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    if x > x1:
        d = min(x - x1, ARM_CORNER_R)
        y -= ARM_CORNER_R - math.sqrt(ARM_CORNER_R ** 2 - d * d)
    return y


def _build_armrest():
    z_low, r = L.CONSOLE_TOP_Z - 0.004, 0.016
    y_front, y_rear = ARM_SEAM_D[1] + 0.004, L.ARMREST_Y0
    rings = []
    n_y, n_x = 46, 26
    for k in range(n_y):
        y = y_front + (y_rear - y_front) * k / (n_y - 1)
        hd, hp = console_half_w(y)
        xl, xr = -hd - 0.008, hp + 0.006
        z_top = 0.628 + 0.008 * (k / (n_y - 1))
        top = []
        for i in range(n_x):
            s = 0.5 - 0.5 * math.cos(math.pi * i / (n_x - 1))     # denser toward the edges
            x = xl + (xr - xl) * s
            # rounded nose: rises steeply from the seam and rolls over into the flat top within ~40 mm (owner photo)
            dn = max(0.0, min(1.0, (_arm_seam_y(x) - y) / 0.042))
            ramp = math.sqrt(max(0.0, 1.0 - (1.0 - dn) ** 2)) ** 1.3
            z = z_low + (z_top + 0.005 * (1 - (2 * s - 1) ** 2) - z_low) * ramp
            dz = min(x - xl, xr - x)                              # roll over the side edges
            if dz < r:
                z -= (r - math.sqrt(max(0.0, r * r - (r - dz) ** 2))) * ramp
            top.append(Vector((x, y, z)))
        bottom = [Vector((xr - 0.008, y, 0.49)), Vector((xl + 0.008, y, 0.49))]
        rings.append(top + bottom)
    # winding chosen so the top faces up (same test as dashboard._loft_needs_flip)
    up_ok = (rings[0][1] - rings[0][0]).cross(rings[1][0] - rings[0][0]).z > 0
    arm = lib.loft_object('console.armrest', rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=3.0, flip=not up_ok)
    lib.add_subsurf(arm, 1)
    lib.tag(arm, 'console.armrest', 'console')


def build(shifter='automatic'):
    build_body()
    build_shifter(shifter)
    build_dial_and_switches()
    build_cupholders_and_armrest()
