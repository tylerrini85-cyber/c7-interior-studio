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
    ys = [0.47, 0.42, 0.36, 0.28, 0.20, 0.12, 0.04, -0.04, -0.10, -0.2, -0.3, -0.4, -0.47, -0.55, L.REAR_BULKHEAD_Y + 0.02]
    rings = [_console_section(y) for y in ys]
    body = lib.loft_object('console.main', rings, close_u=True, cap_start=True, cap_end=True, material='leather_black', uv_scale=1.5)
    lib.add_subsurf(body, 1)
    lib.tag(body, 'console.main', 'console')
    # gloss trim plate on top around the shifter (waterfall continues from the stack)
    plate = lib.extrude_profile('console.trim', lib.rounded_rect2d(0.23, 0.60, 0.02), (0.0, 0.15, L.CONSOLE_TOP_Z + 0.004), (1, 0, 0), (0, 1, 0), 0.006, material='metal_brushed', bevel=0.002)
    lib.tag(plate, 'console.trim', 'console')
    # side accent strips (brushed) along the top edges of the console
    for side in (-1, 1):
        strip = lib.box(f'console.side_trim_{side}', (0.012, 0.95, 0.008), (side * (L.CONSOLE_HALF_W - 0.03), -0.02, L.CONSOLE_TOP_Z + 0.004), material='metal_brushed', bevel=0.002)
        lib.tag(strip, f'console.side_trim.{"driver" if side < 0 else "passenger"}', 'trim', selectable=False)


def build_shifter(variant='automatic'):
    y = L.SHIFTER_Y
    base = Vector((0.0, y, L.CONSOLE_TOP_Z + 0.01))
    if variant == 'automatic':
        # leather boot: truncated pyramid with a soft top collar
        rings = []
        for s, (w, d, h) in ((0.0, (0.11, 0.13, 0.0)), (0.5, (0.07, 0.085, 0.045)), (1.0, (0.038, 0.042, 0.08))):
            prof = lib.rounded_rect2d(w, d, 0.012)
            rings.append(lib.place_profile(prof, base + Vector((0, 0, h)), (1, 0, 0), (0, 1, 0)))
        boot = lib.loft_object('console.shifter.boot', rings, close_u=True, cap_start=True, cap_end=False, material='leather_black', uv_scale=3.0)
        lib.add_subsurf(boot, 1)
        lib.tag(boot, 'console.shifter.boot', 'console')
        # lever + knob (leaning slightly rearward)
        top = base + Vector((0, -0.03, 0.17))
        lever = lib.sweep_tube('console.shifter.lever', [base + Vector((0, 0, 0.07)), top], 0.012, n=16, material='metal_satin_dark')
        lib.tag(lever, 'console.shifter.lever', 'console', selectable=False)
        knob = lib.revolve('console.shifter.knob', [(0.0, 0.0), (0.016, 0.0), (0.020, 0.012), (0.024, 0.035), (0.026, 0.06), (0.024, 0.078), (0.016, 0.088), (0.0, 0.09)], segments=32, material='leather_black', origin=top - Vector((0, 0, 0.01)), direction=(0, -0.18, 1))
        lib.tag(knob, 'console.shifter.knob', 'console')
        ring = lib.revolve('console.shifter.ring', [(0.022, 0.0), (0.027, 0.0), (0.027, 0.012), (0.022, 0.012)], segments=32, material='chrome', origin=top - Vector((0, 0, 0.01)), direction=(0, -0.18, 1))
        lib.tag(ring, 'console.shifter.ring', 'trim', selectable=False)
        # PRNDL indicator strip beside the boot
        ind = lib.extrude_profile('console.shifter.indicator', lib.rounded_rect2d(0.012, 0.10, 0.003), base + Vector((-0.075, 0.0, 0.0)), (1, 0, 0), (0, 1, 0), 0.001, material='screen_off')
        lib.tag(ind, 'console.shifter.indicator', 'electronics', selectable=False)
    else:
        # manual: round boot and taller lever with a spherical knob
        rings = []
        for s, (r, h) in ((0.0, (0.06, 0.0)), (0.5, (0.038, 0.05)), (1.0, (0.02, 0.10))):
            rings.append(lib.place_profile(lib.circle2d(r, 28), base + Vector((0, 0, h)), (1, 0, 0), (0, 1, 0)))
        boot = lib.loft_object('console.shifter.boot', rings, close_u=True, cap_start=True, cap_end=False, material='leather_black', uv_scale=3.0)
        lib.add_subsurf(boot, 1)
        lib.tag(boot, 'console.shifter.boot', 'console')
        h = 0.22 if variant == 'manual' else 0.16
        top = base + Vector((0, -0.02, h))
        lever = lib.sweep_tube('console.shifter.lever', [base + Vector((0, 0, 0.09)), top], 0.011, n=16, material='metal_brushed')
        lib.tag(lever, 'console.shifter.lever', 'console', selectable=False)
        knob = lib.revolve('console.shifter.knob', [(0.0, 0.0), (0.02, 0.0), (0.03, 0.02), (0.028, 0.04), (0.0, 0.05)], segments=32, material='leather_black', origin=top, direction=(0, -0.1, 1), subsurf=1)
        lib.tag(knob, 'console.shifter.knob', 'console')


def build_dial_and_switches():
    # drive mode selector dial (left of / behind the shifter)
    c = Vector((-0.085, L.DIAL_Y + 0.02, L.CONSOLE_TOP_Z + 0.01))
    dial = lib.revolve('console.drive_mode_dial', [(0.0, 0.0), (0.028, 0.0), (0.03, 0.014), (0.027, 0.02), (0.012, 0.022), (0.0, 0.022)], segments=36, material='metal_satin_dark', origin=c, direction=(0, 0, 1))
    lib.tag(dial, 'console.drive_mode_dial', 'console')
    base = lib.revolve('console.drive_mode_base', [(0.0, 0.0), (0.036, 0.0), (0.038, 0.004), (0.0, 0.004)], segments=36, material='plastic_black', origin=c - Vector((0, 0, 0.003)), direction=(0, 0, 1))
    lib.tag(base, 'console.drive_mode_base', 'console', selectable=False)
    # electronic parking brake switch and two buttons on the right
    epb = lib.extrude_profile('console.epb', lib.rounded_rect2d(0.03, 0.045, 0.006), (0.085, L.DIAL_Y + 0.03, L.CONSOLE_TOP_Z + 0.01), (1, 0, 0), (0, 1, 0), 0.006, material='plastic_black', bevel=0.002)
    lib.tag(epb, 'console.epb', 'console', selectable=False)
    for k in range(2):
        b = lib.extrude_profile(f'console.btn_{k}', lib.rounded_rect2d(0.03, 0.018, 0.004), (0.085, L.DIAL_Y - 0.015 - 0.024 * k, L.CONSOLE_TOP_Z + 0.01), (1, 0, 0), (0, 1, 0), 0.004, material='plastic_black')
        lib.tag(b, f'console.btn.{k}', 'console', selectable=False)
    # traction / PDR buttons row at the front of the console below the stack
    for k in range(3):
        b = lib.extrude_profile(f'console.front_btn_{k}', lib.rounded_rect2d(0.03, 0.016, 0.003), (-0.04 + 0.04 * k, 0.42, L.CONSOLE_TOP_Z + 0.011), (1, 0, 0), (0, 1, 0), 0.004, material='plastic_black')
        lib.tag(b, f'console.front_btn.{k}', 'console', selectable=False)


def build_cupholders_and_armrest():
    # cupholder recess: two holes in tandem cut into a plate; sliding cover modelled closed over the rear one
    plate = lib.extrude_profile('console.cupholder_plate', lib.rounded_rect2d(0.11, 0.20, 0.03), (0.0, 0.0, L.CONSOLE_TOP_Z + 0.002), (1, 0, 0), (0, 1, 0), 0.004, material='plastic_black')
    lib.tag(plate, 'console.cupholder_plate', 'console')
    for k, y in enumerate((0.055, -0.03)):
        cutter = lib.revolve(f'cup_cutter_{k}', [(0.0, -0.1), (0.04, -0.1), (0.04, 0.1), (0.0, 0.1)], segments=32, origin=(0, y, L.CONSOLE_TOP_Z), direction=(0, 0, 1))
        lib.add_boolean(plate, cutter)
        # cup well (dark cylinder below)
        well = lib.revolve(f'console.cupholder_{k}', [(0.0, 0.0), (0.038, 0.0), (0.038, 0.07), (0.041, 0.07)], segments=32, material='rubber', origin=(0, y, L.CONSOLE_TOP_Z - 0.068), direction=(0, 0, 1))
        lib.tag(well, f'console.cupholder.{k}', 'console', selectable=False)
    # tambour cover slid partly open (slats)
    for k in range(5):
        slat = lib.box(f'console.cup_cover_{k}', (0.105, 0.014, 0.004), (0.0, -0.075 - k * 0.015, L.CONSOLE_TOP_Z + 0.009), material='plastic_black_gloss', bevel=0.001)
        lib.tag(slat, f'console.cup_cover.{k}', 'console', selectable=False)
    # armrest lid: padded leather pad with rounded edges and a stitched seam
    lid_c = (0.0, (L.ARMREST_Y0 + L.ARMREST_Y1) / 2, L.ARMREST_Z + 0.015)
    lid = lib.box('console.armrest', (0.24, L.ARMREST_Y1 - L.ARMREST_Y0, 0.045), lid_c, material='leather_black', bevel=0.018, bevel_segments=6)
    lib.tag(lid, 'console.armrest', 'console')
    # storage bin front wall under the lid (dark)
    bin_ = lib.box('console.armrest_bin', (0.23, L.ARMREST_Y1 - L.ARMREST_Y0 - 0.02, 0.03), (0.0, lid_c[1], L.ARMREST_Z - 0.02), material='plastic_black')
    lib.tag(bin_, 'console.armrest_bin', 'console', selectable=False)
    # rear of the console: small tray and the two rear vents? (C7 has a rear storage tray)
    tray = lib.extrude_profile('console.rear_tray', lib.rounded_rect2d(0.18, 0.08, 0.02), (0.0, L.ARMREST_Y0 - 0.07, L.CONSOLE_TOP_Z + 0.022), (1, 0, 0), (0, 1, 0), -0.03, material='rubber')
    lib.tag(tray, 'console.rear_tray', 'console', selectable=False)


def build(shifter='automatic'):
    build_body()
    build_shifter(shifter)
    build_dial_and_switches()
    build_cupholders_and_armrest()
