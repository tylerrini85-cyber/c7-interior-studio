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
EYE = (-SEAT_X, -0.12, 0.92)   # driver eye point (reclined posture)
PASSENGER_EYE = (SEAT_X, -0.12, 0.92)

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

DOOR_Y_FRONT = 0.72            # door panel meets dash end
DOOR_Y_REAR = -0.55

TOEBOARD_Y0 = 0.78             # flat floor ends
TOEBOARD_Y1 = 1.06             # toe board meets dash lower
TOEBOARD_Z1 = 0.42

TUNNEL_HALF_W = 0.16
TUNNEL_Z = 0.26

# dashboard
DASH_REAR_Y_CENTER = 0.58      # rear (occupant) edge of the dash top at the centre stack
DASH_TOP_Z = 0.86              # general dash top level
HOOD_TOP_Z = 0.915              # instrument hood crest
HOOD_HALF_W = 0.24
CLUSTER_CENTER = (-SEAT_X, 0.745, 0.775)
CLUSTER_TILT = math.radians(18)
CLUSTER_W = 0.36
CLUSTER_H = 0.16
KNEE_BOLSTER_Z = 0.50

# steering
WHEEL_CENTER = (-SEAT_X, 0.46, 0.645)
WHEEL_TILT = math.radians(24)   # wheel plane tilted so the top is further from the driver
WHEEL_RADIUS = 0.179            # 14.1 in diameter
RIM_RADIUS = 0.0165

# console
CONSOLE_HALF_W = 0.155
CONSOLE_TOP_Z = 0.56           # top at shifter area
ARMREST_Z = 0.60
ARMREST_Y0 = -0.46
ARMREST_Y1 = -0.08
SHIFTER_Y = 0.40
DIAL_Y = 0.12
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
