"""Cockpit packaging constants (meters). Blender frame: +X passenger side, +Y forward, +Z up, floor (heel point) Z=0.

Derived from published 2019 Stingray figures (headroom 37.9 in effective, legroom 43 in, shoulder 55.2 in,
hip 53.7 in, height 48.6 in, width 73.9 in) plus SAE J1100 conventions. Every value is APPROX pending photo
validation — see docs/REFERENCES.md item 12.
"""
import math

FLOOR_Z = 0.0
SEAT_X = 0.37                  # driver seat centre at -SEAT_X, passenger at +SEAT_X
HIP_Y = 0.0                    # seating reference point (H-point)
HIP_Z = 0.26
EYE = (-SEAT_X, -0.12, 0.96)   # driver eye point (reclined posture)
PASSENGER_EYE = (SEAT_X, -0.12, 0.96)

HEADLINER_Z = 1.10             # underside of headliner at cabin centre over the seats
HEADLINER_SIDE_Z = 1.03        # at X = +-0.60
ROOF_HALF_W = 0.66             # roof rail inner edge
TARGA_HALF_W = 0.50            # removable panel half width
TARGA_Y_FRONT = 0.30
TARGA_Y_REAR = -0.48

HEADER_Y = 0.38                # windshield top / roof front edge
HEADER_Z = 1.08
COWL_Y = 1.08                  # windshield base (dash top meets glass)
COWL_Z = 0.82
WINDSHIELD_HALF_W_TOP = 0.60
WINDSHIELD_HALF_W_BASE = 0.73

HALO_Y = -0.55                 # B-pillar hoop centre plane
HALO_DEPTH = 0.10
REAR_BULKHEAD_Y = -0.64
CARGO_FLOOR_Z = 0.50
REAR_GLASS_END = (-1.45, 0.78)  # (Y, Z) of rear glass lower edge

CABIN_HALF_W_HIP = 0.685       # inner door surface at hip height
CABIN_HALF_W_SHOULDER = 0.70
SILL_Z = 0.82                  # door window sill (beltline) above heel point
ROCKER_HALF_W = 0.70
ROCKER_TOP_Z = 0.16
ROCKER_W = 0.12

DOOR_Y_FRONT = 0.82            # door panel front edge runs on past the dash end so its open end is hidden
DOOR_Y_REAR = -0.55

TOEBOARD_Y0 = 0.78             # flat floor ends
TOEBOARD_Y1 = 1.06             # toe board meets dash lower
TOEBOARD_Z1 = 0.42

TUNNEL_HALF_W = 0.16
TUNNEL_Z = 0.26

# dashboard
DASH_REAR_Y_CENTER = 0.58      # rear (occupant) edge of the dash top at the centre stack
DASH_TOP_Z = 0.86              # general dash top level
HOOD_TOP_Z = 0.885              # instrument hood crest (below the eye line so the dash top is visible)
HOOD_HALF_W = 0.24
CLUSTER_CENTER = (-SEAT_X, 0.745, 0.775)
CLUSTER_TILT = math.radians(18)
CLUSTER_W = 0.36
CLUSTER_H = 0.16
KNEE_BOLSTER_Z = 0.50

# steering
WHEEL_CENTER = (-SEAT_X, 0.45, 0.705)
WHEEL_TILT = math.radians(24)   # wheel plane tilted so the top is further from the driver
WHEEL_RADIUS = 0.179            # 14.1 in diameter
RIM_RADIUS = 0.0165

# console
CONSOLE_HALF_W = 0.155          # driver side
CONSOLE_HALF_W_PASS = 0.195     # passenger side: runs out under the grab band, in line with it from the stack (B38)
CONSOLE_TOP_Z = 0.56           # top at shifter area
ARMREST_Z = 0.60
ARMREST_Y0 = -0.40
ARMREST_Y1 = 0.02
SHIFTER_Y = 0.40
SHIFTER_X = -0.050             # shifter sits on the driver half of the console (B37 / B44)
DIAL_Y = 0.24
SCREEN_CENTER = (0.0, 0.66, 0.74)
SCREEN_W = 0.19
SCREEN_H = 0.115
STACK_YAW = math.radians(-18)   # centre stack rotated toward the driver (negative = toward -X)

# seats (GT)
SEAT_W = 0.52
CUSHION_Y0 = -0.26
CUSHION_Y1 = 0.26
CUSHION_TOP_Z = 0.30
SEATBACK_RECLINE = math.radians(23)
SEATBACK_H = 0.66              # pivot to shoulder top
HEADREST_TOP_Z = 1.01

# doors
ARMREST_DOOR_Z = 0.58
ARMREST_DOOR_PROTRUSION = 0.09
DOOR_HANDLE_Z = 0.70
SPEAKER_CENTER = (0.35, 0.26)   # (Y, Z)


# beside the seat cushions the console's side walls stop just above the cushion's inner bolster (top ~0.38) and the
# console's lower side steps in behind the cushion, so the seats tuck under the console edge instead of the walls
# running through them
SEAT_SIDE_Z = 0.405


def seat_zone(y):
    """1 alongside the seat cushions, 0 clear of them (eased over 4 cm at each end)."""
    def ss(a, b, x):
        t = max(0.0, min(1.0, (x - a) / (b - a)))
        return t * t * (3 - 2 * t)
    return ss(CUSHION_Y1 + 0.07, CUSHION_Y1 + 0.03, y) * ss(CUSHION_Y0 - 0.07, CUSHION_Y0 - 0.03, y)

