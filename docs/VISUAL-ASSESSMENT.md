# Visual assessment against owner-supplied reference photos

Reference set: 23 photos in `reference/` (IMG_4491..4516; 4518 is the crossed-flags artwork) covering driver and
passenger views, the cluster, center stack, console, seats (GT and Competition, several colors), door panels,
dash trim and the removable roof. App captures: `docs/renders-web/01..10` (software WebGL, High preset).

## What the photos changed (applied in the Blender scripts)
| Area | Photo evidence | Change made |
|------|----------------|-------------|
| Steering wheel | 4495, 4511, 4514, 4515, 4516: one satin-silver Y frame (two arms + stem), black switch pods inset at the arm ends, true flat bottom with a trim insert, pointed shield airbag with crossed flags | Rebuilt: Y frame plates, pods with 3 buttons, flat-bottom rim with insert, shield hub, emblem badge carrying the supplied artwork |
| Cluster | 4512, 4495: three separate tunnels under one hood (big speedo, 8-in LCD, small right dial) | Added dial rings and a center frame in front of the glass |
| Dash trim | 4491, 4509, 4496: a ~11 cm tall sculpted trim panel on each side carrying tall vertical vents; passenger side has a second vent beside the stack plus a seat-heat switch panel | Thin strip replaced by tall panels with bright edges; tall vents (3 vanes + bezel); inner passenger vent and switch panel added |
| Grab handle | 4499, 4513, 4494: wide aluminium fin from dash top down the passenger side of the stack with a leather pad on top | Leather tube replaced by an aluminium fin with a leather top pad |
| Console | 4493, 4499, 4513, 4508: one long bright plate from the HVAC past the shifter, dial and EPB to the cupholders; tall leather-wrapped knob with chrome ring | Plate lengthened to 0.60 m, factory finish aluminium; knob reshaped |
| Seats | 4500, 4507, 4497, 4513: smooth perforated inserts with a stitched border (no pleats), strong shoulder wings, horizontal pass-through slot under the headrest pad, flags badge on the bridge | Pleats removed, slot cut with a liner, emblem decal on the headrest bridge |
| Doors | 4509, 4499, 4516: aluminium V grab handle rising from the armrest front, silver release lever above it, hex tweeter sail by the mirror, switches on the armrest | Leather bridge replaced by an aluminium V-handle with opening, release lever moved above it, tweeter sail added |

## Remaining discrepancies (visible in the photos, not yet modeled)
- Dash stitching path and the exact curvature of the hood/binnacle; the real hood is lower and broader.
- Door panel: the diagonal character line and the sweeping upper pad shape are simplified; the window-switch
  pod is a flat plate rather than the real sculpted housing.
- Seat bolster sculpt is still smoother than the real GT seat; the Competition seat variant does not yet have the
  full one-piece shoulder wrap.
- Center stack: screen-side power/volume knob and SCREEN button are present only as generic buttons.
- No exterior; the halo and rear hatch are simplified.

## Second pass (owner review of the first pass, IMG_4499 / 4495 / 4506 / 4491 / 4509 / 4493 / 4516)
| Owner finding | What was wrong | Change made |
|---------------|----------------|-------------|
| Wheel should be round; flat bottom as an option | Factory rim had a flat segment; paddles were in front of the rim; arms were horizontal bars | Factory rim is now fully round; "Flat-bottom (Z06 / ZR1 style)" is a variant; arms rise from the hub to the rim at 9:30 / 2:30 with the switch pods at their ends; paddles sit behind the rim |
| Center stack does not connect to the console | Stack was a thin floating plate with a gap above the console plate | Stack is one solid rearward-leaning body from under the dash lip down to a waterfall that meets the console plate; the badge lip sits where the face turns horizontal |
| Area around the screen is wrong | Screen and chunky vents hovering on rods | Gloss surround with the volume knob and SCREEN button on its left, 8-in screen, media row (two knobs, five buttons), climate row (two knobs, eight buttons); two slim top vents with the hazard / airbag pod between |
| Passenger side not accurate | Wide aluminium fin hanging in space; vent parts buried inside the pad; trim band culled | Thin aluminium grab blade that stands off the stack face in the middle and continues as the console plate edge, with a stitched leather ridge outboard of it; trim bands rebuilt as solids with bright edges; vents rebuilt flush with louvres, slider and bezel; outer passenger vent is the short one with the seat switches under it |

Still approximate: dash-top sculpting between the hood and the passenger pad, the exact stack edge curvature, and the
knee bolster / glovebox split line on the passenger lower dash.

## Third pass (owner review: screen, emblem, shifter)
| Owner finding | Change made |
|---------------|-------------|
| Screen should show the Corvette logo | Factory infotainment home is the crossed flags on black with temperature and clock in the status strip (IMG_4506); both screens now get a true planar projection of their face, which also fixed the cluster showing only a corner of its artwork |
| Wheel logo without the rectangle, bigger | Emblem carrier plate removed; the artwork is a transparent decal straight on the airbag cover, 58 mm wide (IMG_4499/4516) |
| Gear shift far too big | A8 shifter rebuilt to photo scale: 90 x 110 mm boot 38 mm tall, short lever, 45 mm leather knob with a chrome collar, about 140 mm above the plate (IMG_4508/4499); manual variants scaled to match |

## Fourth pass (owner review: screen UI, passenger bar, seats)
| Owner finding | Change made |
|---------------|-------------|
| Screen should match the photos | Factory home is now the MyLink layout from IMG_4499 / 4495: status strip with temperature and clock, two rows of app tiles (Audio, Phone, Projection, Nav, Settings, Weather, PDR, Text) with icon glyphs, page arrows |
| The bar on the passenger side of the centre is not on the real car | The round leather ridge beside the grab blade was removed; the blade now sits almost flush on the stack like IMG_4499 / 4506 |
| Bucket seats need to match the photos | GT seat rebuilt from IMG_4500 / 4507 / 4497 / 4513 / 4503 / 4504: one-piece hooded backrest with the headrest integrated (wide shoulders tapering to a rounded crown), stitched rounded-top headrest pad with the flags badge at its foot, 165 x 45 mm pass-through slot with a dark liner, wide perforated centre inserts on both cushion and back with a bordered seam, deep wrapped bolsters that fade out toward the hood, lumbar push, plastic back shell, outboard trim with three switches; no embroidered text by default |

## Fifth pass (owner review: seat badge, stack angle and screen size)
| Owner finding | Change made |
|---------------|-------------|
| Seat badge should be on the headrest and much bigger | Badge is a 72 mm decal centred on the headrest pad, placed from the seat layout rather than the mesh bounds |
| Stack should be slanted toward the driver, screen bigger and in the middle | Stack body narrowed to about 33 cm and yawed 14 degrees toward the driver over its full height; screen enlarged to 215 x 128 mm and centred with the power / SCREEN strip in its own narrow panel on the left; media row widened; climate knobs enlarged with dark display faces and two rows of four buttons between them; top vents, start button, inner passenger vent and trim band moved to suit |

## Sixth pass (owner: "nothing changed")
| Finding | Change made |
|---------|-------------|
| Stack still read as plates on a curved body, not one flat angled panel | Stack face is now a single plane from the top vents to the climate row (waterfall only at the foot), yawed 18 degrees toward the driver over its full height; screen bezel, media and climate panels sit flush in that plane with only knobs and buttons standing proud; screen enlarged to 232 x 138 mm |
| Live site could keep showing the old model after a deploy | Model files are requested with a build id (`?v=`) so a normal reload fetches new geometry; GitHub Pages caches the fixed-name files for ten minutes otherwise |

Verdict: the cockpit now matches the C7 photos in layout, proportion and the signature elements (Y-spoke wheel,
hooded three-tunnel cluster, driver-angled stack with grab fin, long aluminium console plate, GT seats with
headrest slot, aluminium door handles). Surface-level sculpting and stitching detail remain approximations.
