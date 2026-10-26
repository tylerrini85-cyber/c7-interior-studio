"""Door panels (driver, passenger mirrored): upper pad, armrest with pull handle, release handle, window/lock switch
panel, speaker, map pocket, trim band, courtesy lamp, sill plate."""
import math
from mathutils import Vector
import lib
import layout as L


def _panel_section(y, side):
    """Open polyline (bottom -> top) of the inner door surface at station y, in X-Z; side = -1 driver, +1 passenger.
    Shape: lower moulded panel, padded armrest shelf, concave upper pad, thick rolled top bolster at the sill."""
    x_hip = L.CABIN_HALF_W_HIP
    x_sh = L.CABIN_HALF_W_SHOULDER
    s = (y - L.DOOR_Y_REAR) / (L.DOOR_Y_FRONT - L.DOOR_Y_REAR)
    arm_z = L.ARMREST_DOOR_Z
    bulge = math.sin(math.pi * min(1.0, max(0.0, (s - 0.10) / 0.80)))
    arm_in = L.ARMREST_DOOR_PROTRUSION * (0.30 + 0.70 * bulge)
    pts = [
        (x_hip + 0.03, L.ROCKER_TOP_Z + 0.02),
        (x_hip + 0.028, 0.30),
        (x_hip + 0.022, 0.42),
        (x_hip + 0.012, arm_z - 0.10),
        (x_hip - arm_in * 0.55, arm_z - 0.075),      # underside of the armrest shelf
        (x_hip - arm_in, arm_z - 0.035),
        (x_hip - arm_in - 0.004, arm_z + 0.0),        # rounded front edge
        (x_hip - arm_in * 0.55, arm_z + 0.018),       # flat padded top
        (x_hip - 0.012, arm_z + 0.022),
        (x_hip - 0.006, arm_z + 0.06),                # upper pad, slightly concave
        (x_hip - 0.0, 0.72),
        (x_sh - 0.03, 0.765),                         # rolled top bolster
        (x_sh - 0.045, L.SILL_Z - 0.02),
        (x_sh - 0.02, L.SILL_Z + 0.004),
        (x_sh + 0.03, L.SILL_Z + 0.004),
    ]
    return [Vector((side * x, y, z)) for x, z in pts]


def build_door(side):
    name = 'driver' if side < 0 else 'passenger'
    prefix = f'doors.{name}'
    ys = [L.DOOR_Y_REAR, -0.45, -0.3, -0.15, 0.0, 0.15, 0.3, 0.45, 0.58, L.DOOR_Y_FRONT]
    rings = [_panel_section(y, side) for y in ys]
    panel = lib.loft_object(f'{prefix}.panel', rings, close_u=False, material='leather_black', uv_scale=1.5, flip=side < 0)
    lib.add_subsurf(panel, 1)
    lib.tag(panel, f'{prefix}.panel', 'doors')
    # upper pad (leather) as a separate overlay strip above the trim band (for independent customisation)
    up_rings = []
    for y in ys:
        r = _panel_section(y, side)
        up_rings.append([p - Vector((side * 0.004, 0, 0)) for p in r[9:15]])
    upper = lib.loft_object(f'{prefix}.upper', up_rings, close_u=False, material='leather_black', uv_scale=1.5, flip=side < 0)
    lib.add_subsurf(upper, 1)
    lib.tag(upper, f'{prefix}.upper', 'doors')
    # lower panel overlay (carpet/plastic) below the armrest
    lo_rings = []
    for y in ys:
        r = _panel_section(y, side)
        lo_rings.append([p - Vector((side * 0.004, 0, 0)) for p in r[0:5]])
    lower = lib.loft_object(f'{prefix}.lower', lo_rings, close_u=False, material='plastic_black', uv_scale=1.5, flip=side < 0)
    lib.tag(lower, f'{prefix}.lower', 'doors')
    # armrest top pad (separate object): follows the bulge between y=-0.30 and y=0.45
    arm_rings = []
    for y in (-0.30, -0.15, 0.0, 0.15, 0.30, 0.45):
        r = _panel_section(y, side)
        arm_rings.append([p + Vector((0, 0, 0.004)) for p in r[4:10]])
    arm = lib.loft_object(f'{prefix}.armrest', arm_rings, close_u=False, material='leather_black', uv_scale=2.0, flip=side < 0)
    lib.add_subsurf(arm, 1)
    lib.tag(arm, f'{prefix}.armrest', 'doors')
    # pull handle: a sculpted grab at the front of the armrest (curved bar rising into the panel)
    x_in = side * (L.CABIN_HALF_W_HIP - L.ARMREST_DOOR_PROTRUSION - 0.01)
    # pull handle: a padded bridge across the front of the armrest top with a hand opening beneath it
    arm_front = L.CABIN_HALF_W_HIP - L.ARMREST_DOOR_PROTRUSION
    bridge = [Vector((side * (arm_front + 0.004), 0.26, L.ARMREST_DOOR_Z + 0.026)), Vector((side * (arm_front - 0.008), 0.34, L.ARMREST_DOOR_Z + 0.036)), Vector((side * (arm_front - 0.006), 0.42, L.ARMREST_DOOR_Z + 0.055)), Vector((side * (arm_front + 0.035), 0.49, L.ARMREST_DOOR_Z + 0.095)), Vector((side * (arm_front + 0.06), 0.53, L.ARMREST_DOOR_Z + 0.125))]
    bridge = lib.spline_through(bridge, n_per_seg=4)
    pull = lib.sweep_tube(f'{prefix}.pull', bridge, (0.024, 0.016), n=16, cap=True, material='leather_black', up_hint=Vector((0, 0, 1)), uv_scale=3.0)
    lib.tag(pull, f'{prefix}.pull', 'doors')
    opening = lib.box(f'{prefix}.pull_recess', (0.06, 0.16, 0.045), (side * (arm_front + 0.02), 0.36, L.ARMREST_DOOR_Z - 0.0), material='plastic_black')
    lib.tag(opening, f'{prefix}.pull_recess', 'doors', selectable=False)
    # window / lock switch panel on top of the armrest
    sw = lib.extrude_profile(f'{prefix}.switches', lib.rounded_rect2d(0.05, 0.11, 0.01), (x_in + side * 0.02, 0.05, L.ARMREST_DOOR_Z + 0.024), (1, 0, 0), (0, 1, 0), 0.004, material='plastic_black_gloss', bevel=0.002)
    lib.tag(sw, f'{prefix}.switches', 'doors', selectable=False)
    for k in range(2):
        b = lib.box(f'{prefix}.winsw_{k}', (0.022, 0.03, 0.01), (x_in + side * 0.02, 0.08 - 0.035 * k, L.ARMREST_DOOR_Z + 0.03), material='plastic_black', bevel=0.003)
        lib.tag(b, f'{prefix}.winsw.{k}', 'doors', selectable=False)
    # door release handle: flush lever in the upper pad near the front
    rel = lib.extrude_profile(f'{prefix}.handle', lib.rounded_rect2d(0.11, 0.028, 0.012), (side * (L.CABIN_HALF_W_SHOULDER - 0.03), 0.47, L.DOOR_HANDLE_Z), (0, 1, 0), (0, 0, 1), side * -0.012, material='metal_satin_dark', bevel=0.003)
    lib.tag(rel, f'{prefix}.handle', 'doors')
    bezel = lib.extrude_profile(f'{prefix}.handle_bezel', lib.rounded_rect2d(0.14, 0.05, 0.02), (side * (L.CABIN_HALF_W_SHOULDER - 0.018), 0.47, L.DOOR_HANDLE_Z), (0, 1, 0), (0, 0, 1), side * 0.03, material='plastic_black')
    lib.tag(bezel, f'{prefix}.handle_bezel', 'doors', selectable=False)
    # speaker grille (round) low in the front of the door
    sy, sz = L.SPEAKER_CENTER
    spk = lib.revolve(f'{prefix}.speaker', [(0.0, 0.0), (0.085, 0.0), (0.09, 0.006), (0.0, 0.006)], segments=40, material='plastic_black', origin=(side * (L.CABIN_HALF_W_HIP + 0.02), sy, sz), direction=(-side, 0, 0))
    lib.tag(spk, f'{prefix}.speaker', 'doors')
    ring = lib.revolve(f'{prefix}.speaker_ring', [(0.085, 0.0), (0.095, 0.0), (0.095, 0.008), (0.085, 0.008)], segments=40, material='metal_brushed', origin=(side * (L.CABIN_HALF_W_HIP + 0.02), sy, sz), direction=(-side, 0, 0))
    lib.tag(ring, f'{prefix}.speaker_ring', 'trim', selectable=False)
    # map pocket: open bin along the lower door
    pocket = lib.box(f'{prefix}.pocket', (0.05, 0.45, 0.10), (side * (L.CABIN_HALF_W_HIP - 0.0), -0.12, 0.30), material='plastic_black', bevel=0.008)
    lib.tag(pocket, f'{prefix}.pocket', 'doors')
    # trim band (brushed) running along the top of the armrest line toward the dash
    band_rings = []
    for y in (L.DOOR_Y_REAR + 0.05, -0.2, 0.1, 0.4, L.DOOR_Y_FRONT - 0.02):
        r = _panel_section(y, side)
        p = r[9]
        band_rings.append([Vector((p.x - side * 0.004, p.y, p.z + 0.012)), Vector((p.x - side * 0.004, p.y, p.z - 0.012))])
    band = lib.loft_object(f'{prefix}.trim', band_rings, close_u=False, material='metal_brushed', flip=side > 0)
    lib.add_solidify(band, 0.004, offset=1.0)
    lib.tag(band, f'{prefix}.trim', 'trim')
    # courtesy lamp near the bottom rear and the sill plate
    lamp = lib.box(f'{prefix}.lamp', (0.01, 0.04, 0.012), (side * (L.CABIN_HALF_W_HIP + 0.02), -0.40, 0.22), material='emissive_white')
    lib.tag(lamp, f'lighting.door.{name}', 'lighting', selectable=False)
    sill = lib.box(f'{prefix}.sill_plate', (0.09, 0.9, 0.004), (side * (L.ROCKER_HALF_W - 0.06), 0.08, L.ROCKER_TOP_Z + 0.002), material='metal_brushed', bevel=0.001)
    lib.tag(sill, f'{prefix}.sill_plate', 'trim', selectable=False)


def build():
    build_door(-1)
    build_door(1)
