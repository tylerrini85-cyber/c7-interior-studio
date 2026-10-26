# Visual self-assessment (automated captures, software WebGL, "high" quality)

Captures: `docs/renders-web/01..10-*.png` produced by `tests/render-views.cjs` (factory Jet Black project, showroom
environment). Blender geometry check renders: `docs/renders/*.png`. No reference photographs were available in this
environment (network policy), so comparisons below are against my knowledge of the 2014–2019 C7 cockpit and the
published figures in `docs/REFERENCES.md`. **Every row needs a human check against real photos before the interior can
be called visually complete.**

| # | View | Recognizable C7 traits present | Gaps / discrepancies | Gate status |
|---|------|-------------------------------|----------------------|-------------|
| 1 | Driver POV | Low seating position, hooded cluster with analog speedo + 8-in display + fuel/temp, 14.1-in three-spoke wheel with thumb rests and metal pods, column stalks, driver-angled stack with 8-in screen, HVAC strip, passenger grab bar, trim band, raked windshield, visors, mirror | Dash stitch line not modeled; door panel reads flat; hood lip simplified; no exterior body through glass | Needs photo check |
| 2 | Passenger POV | Angled stack seen from the right, grab handle beside it, flat passenger upper dash with trim band and glovebox panel, outer vent | Passenger airbag seam and dash stitch absent | Needs photo check |
| 3 | Dash front | Driver-oriented asymmetry, two seats with integrated headrests, tunnel console with armrest lid, both door armrests | Lower dash is a dark mass; footwell detail minimal | Needs photo check |
| 4 | Wheel close-up | Rim thickness, spoke layout, pods, shield airbag, paddles behind | Airbag cover too smooth; placeholder badge barely visible; button graphics absent | Needs photo check |
| 5 | Center console | Shifter with boot and chrome ring, drive-mode dial, EPB/buttons, tandem cupholders, armrest lid, side accents | Cupholder cover not animated; PRNDL indicator plain | Needs photo check |
| 6 | Driver seat | Sculpted base with bolsters, tapered bolstered back, neck + headrest, back shell, inboard buckle | Surface sculpt simplified; no seam geometry (stitch texture only) | Needs photo check |
| 7 | Passenger seat | Same as 6 | Same as 6 | Needs photo check |
| 8 | Door panel | Upper pad, trim band, armrest with switch panel, pull handle, release handle, speaker ring, pocket | Pull handle sculpt is basic; panel large and flat; no stitching path | Weakest area |
| 9 | Headliner | Suede headliner, overhead console, targa panel seam, visors, header | Map lights/dome plain; roof-panel latches absent | Acceptable |
| 10 | Rear view | Halo bar behind seats, rear strip, hatch glass, quarter trims, cargo floor | Rear cabin trim simplified; no cargo shade | Acceptable |

Material response checks (from the same captures): leather shows grain and soft specular, brushed pods show
anisotropic streaks, screens emit with correct orientation, carbon knob shows weave (variant preview). Night + RGB
capture (`tests` run, `/tmp/c7-e2e/night-rgb.png`) confirmed zone lights illuminate dash, console, footwells and doors.

Verdict: the interior is **recognizably a C7-style cockpit in layout and proportion**, not photoreal, and not yet
validated against photographs. Visual approval gate: **open** pending Tyler's review and reference photos.
