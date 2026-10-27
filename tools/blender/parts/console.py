"""Centre console (automatic): tunnel console body, shifter plate, A8 shifter with boot, drive-mode dial, EPB switch,
cupholders with sliding cover, armrest lid, side trims. Manual variant swaps the shifter."""
import math
from mathutils import Vector
import lib
import layout as L

SHIFTER_VARIANTS = ['automatic', 'manual', 'short_throw']


def _console_section(y):
    """Closed ring (X-Z) of the console body at station y."""
    hw = L.CONSOLE_HALF_W
    # top height varies: 0.56 at the shifter area rising to 0.585 under the armrest
    top = L.CONSOLE_TOP_Z + 0.025 * lib.__dict__.get('smooth', lambda a, b, x: max(0, min(1, (x - a) / (b - a))))(0.0, -0.12, y) if False else L.CONSOLE_TOP_Z
    if y < -0.08:
        top = L.CONSOLE_TOP_Z + 0.02 * min(1.0, (-0.08 - y) / 0.08)
    base_z = 0.10
    pts = [
        (-hw - 0.06, base_z), (-hw - 0.02, base_z + 0.02), (-hw, 0.30), (-hw + 0.005, 0.46), (-hw + 0.02, top - 0.02), (-hw + 0.05, top),
        (-hw + 0.10, top + 0.003), (0.0, top + 0.004), (hw - 0.10, top + 0.003), (hw - 0.05, top), (hw - 0.02, top - 0.02),
        (hw - 0.005, 0.46), (hw, 0.30), (hw + 0.02, base_z + 0.02), (hw + 0.06, base_z), (0.0, base_z - 0.02),
    ]
    return [Vector((x, y, z)) for x, z in pts]


def build_body():
    ys = [0.60, 0.55, 0.50, 0.46, 0.42, 0.36, 0.28, 0.20, 0.12, 0.04, -0.04, -0.10, -0.2, -0.3, -0.38, -0.44, -0.48, -0.50]
    rings = [_console_section(y) for y in ys]
    body = lib.loft_object('console.main', rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=1.5)
    lib.add_subsurf(body, 1)
    lib.tag(body, 'console.main', 'console')
    # brushed plate on the driver half: carries the shifter, the drive-mode dial and the EPB (B37 / B44 / B38)
    plate = lib.extrude_profile('console.trim', lib.rounded_rect2d(0.122, 0.340, 0.018), (-0.052, 0.300, L.CONSOLE_TOP_Z + 0.004), (1, 0, 0), (0, 1, 0), 0.006, material='metal_brushed', bevel=0.002)
    lib.tag(plate, 'console.trim', 'console')
    # small switch square at the front of the passenger half, beside the shifter
    sq = lib.extrude_profile('console.small_switches', lib.rounded_rect2d(0.050, 0.042, 0.006), (0.058, 0.420, L.CONSOLE_TOP_Z + 0.004), (1, 0, 0), (0, 1, 0), 0.006, material='plastic_black_gloss', bevel=0.002)
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
    lid = lib.extrude_profile('console.cupholder_plate', lib.rounded_rect2d(0.098, 0.330, 0.016), (0.058, 0.205, L.CONSOLE_TOP_Z + 0.002), (1, 0, 0), (0, 1, 0), 0.006, material='plastic_black_gloss', bevel=0.002)
    lib.tag(lid, 'console.cupholder_plate', 'console')
    # armrest lid: padded leather pad with rounded edges and a stitched seam
    lid_c = (0.0, (L.ARMREST_Y0 + L.ARMREST_Y1) / 2, L.ARMREST_Z + 0.015)
    lid = lib.box('console.armrest', (0.34, L.ARMREST_Y1 - L.ARMREST_Y0, 0.048), lid_c, material='leather_black', bevel=0.020, bevel_segments=6)
    lib.tag(lid, 'console.armrest', 'console')
    # storage bin front wall under the lid (dark)
    bin_ = lib.box('console.armrest_bin', (0.30, L.ARMREST_Y1 - L.ARMREST_Y0 - 0.02, 0.03), (0.0, lid_c[1], L.ARMREST_Z - 0.02), material='plastic_black')
    lib.tag(bin_, 'console.armrest_bin', 'console', selectable=False)


def build(shifter='automatic'):
    build_body()
    build_shifter(shifter)
    build_dial_and_switches()
    build_cupholders_and_armrest()
