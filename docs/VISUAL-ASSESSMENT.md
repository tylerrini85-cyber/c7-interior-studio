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

## Seventh pass (owner: stack angle and grab bar)
| Owner finding | Change made |
|---------------|-------------|
| Stack slanted about 65 degrees, should be about 80 | Face is now about 79 degrees from horizontal from the top vents to the climate row; the curve into the console happens only at the foot. The dash pad region behind the stack was pushed back to suit, and the console plate and body extended forward to meet the foot |
| The bar on the passenger side stands off the centre piece with a gap behind it | The aluminium bar is a real grab handle: 28 x 8 mm section, attached at the dash top and at the console edge, standing up to 38 mm off the stack edge in between so there is an open gap behind it |
| Stack was turned toward the passenger | Yaw sign fixed; the face turns 18 degrees toward the driver |

## Eighth pass (owner: seat badge, bucket depth, straight bar, screen logo)
| Owner finding | Change made |
|---------------|-------------|
| Seat badge missing | Badge position now comes from the headrest pad mesh itself (x and height from its bounds, depth from its frontmost vertices), so it sits on the head pad for every seat variant; a saved headrest text other than blank or "C7" still replaces it by design |
| Seats too flat, shape good | Back bolsters deepened to 105 mm with the shoulder wings reaching furthest forward and a shallow trough down the centre; cushion bolsters deepened to 85 mm with a dished centre |
| Passenger bar should be straight and extend further | Bar is a straight 30 x 9 mm bar parallel to the stack face, 40 mm off it, from the dash lip past the foot, then along the console plate edge back to the armrest |
| Logo on the centre screen with CORVETTE under it | Factory screen shows the crossed flags with the CORVETTE wordmark beneath, temperature and clock in the strip |

## Ninth pass (owner: control block and the foot of the stack)
| Owner finding | Change made |
|---------------|-------------|
| Only two knobs on the real car, the rest buttons; controls spilling onto the leather; bad transition into the console | One black control panel under the screen with two chrome-rimmed knobs at its sides spanning both rows; row 1 RADIO, MEDIA, home, round MENU, previous, next, BACK; row 2 A/C, four mode buttons, rear defrost, SYNC; the badge strip sits at the foot; console plate pulled back to start where the foot ends and the button row in front of the shifter removed |

## Tenth pass (owner: shifter distance and button placement, matched to the reference photo)
| Owner finding | Change made |
|---------------|-------------|
| Shifter far too far from the screen | Shifter moved forward to 0.40 m (boot starts at the foot of the stack), lever raised so the knob reaches the climate rows like the photo |
| Buttons in the wrong places | Laid out from the photo: media row 16 mm under the bezel (RADIO, MEDIA, home, round MENU, prev, next, BACK at 26 mm pitch), two 42 mm knobs at the panel sides centred between the media row and climate row A, climate row A of five (A/C, face, face+feet, rear defrost, SYNC) and row B of three under its middle (feet, feet+defrost, front defrost), the control panel running down to a CORVETTE badge plate left of centre with a small switch on the right; flat face extended down to 0.566 so nothing sits on the foot curve |

## Reset pass (owner review: survey everything against the photos, fix root causes)
Method: captured driver POV, passenger POV, overhead and rear views before touching geometry, listed the deltas against
the photos, fixed them in the layout constants and builders rather than by patching parts, then re-captured every view.

| Area | What was wrong | Change made |
|------|----------------|-------------|
| Driver view | Eye point too low and the instrument hood crest too high, so the hood blocked the dash; wheel sat low | Eye raised to 0.96 m, hood crest lowered to 0.885 m with a thin visor lip, wheel centre raised 4 cm; the dash top is now visible over the wheel |
| Centre console | Body, plate and trims ran 0.5 m behind the seats to the bulkhead | Console body ends 0.50 m behind the hip point; plate 0.47 m long; cupholders and armrest moved forward; rear tray removed |
| Passenger dash | Outer vent clipped by the dash end cap; a separate switch pad floated below it; the glovebox was a proud slab | Dash narrowed to the door surface (±0.70 m); the outer vent is one tall bezel with louvres above and the two seat switches below (IMG_4509); glovebox is a flush seam outline; door front raised and extended so the band end dies into the door sail |
| Screen and controls | Screen too wide; buttons as blank blocks in the wrong places | True 8-inch screen (190 x 107 active) in a 218 x 126 bezel; control panel is a flat black panel carrying a label overlay with the real key layout (RADIO, MEDIA, home, MENU, previous, next, BACK; A/C, face, face+feet, rear defrost, SYNC; feet, feet+defrost, front defrost; AUTO and FAN by the knobs) and two chrome-rimmed knobs |
| Floor mats | Flat rectangles | Shaped mats 12 mm thick lying on the carpet, embroidered CORVETTE at the heel end with the flags ahead of it; new "Floor mat edges" lighting zone (colour, brightness) and a "Floor mat sparkle" option (colours, count, twinkle) in the Lighting panel; the sparkle sampler now works on floor surfaces |

Verified after the pass: driver, passenger, overhead, rear and door-junction captures; unit tests 16/16; browser walkthrough 20/20.

## Door and passenger dash pass (IMG_4509 / IMG_4499 / IMG_4516)
New photos could not be downloaded in this session (the environment's network policy refuses image hosts), so this
pass used the owner's existing set.

| Area | What was wrong | Change made |
|------|----------------|-------------|
| Door handle | A boxy pull block plus a separate release lever in its own bezel | One satin fin rising from the front of the armrest to a wide head under the tweeter, with the release lever inside the head opening and a dark hand pocket behind it |
| Door accent | Horizontal strip along the armrest, partly buried in the panel | Diagonal bright line from below the tweeter down and rearward across the upper pad, placed by ray-casting the smoothed door surface |
| Door switches, tweeter | Switches mid-armrest; tiny flat sail | Two-switch pod at the root of the fin; larger rounded triangular tweeter sail with a thin bright rim |
| Door speaker | Bright aluminium ring at knee height (not on the car) | Dark surround by default |
| Passenger dash | A plank standing off the dash with bright edges; a glovebox outline (the C7 has no glovebox) | Flush leather panels with a stitched seam bead on a lower edge that sweeps up toward the door; glovebox removed; vents set nearly flush |
| Stitch overlay | Tiled single-stitch texture drew dashed lines across the dash and doors | Off by default on the dash pad, door panels and door armrests (their seams are modelled); still selectable |

## Batch 2 pass (66 owner photos in reference/batch2)
The second batch shows the cabin from the angles the app uses (overhead from behind the seats, driver wide, driver
door, wheel straight on, stack close-up). It revealed architecture that the first set did not show clearly.

| Area | Photo evidence | What was wrong | Change made |
|------|----------------|----------------|-------------|
| Passenger grab handle | B49, B38, B37, B13 | A thin bar beside the stack | A wide leather hoop (about 58 x 64 mm) that leaves the dash top at the stack's passenger corner, stands off the stack with an open gap, and turns rearward into the console's passenger side wall and the armrest; brushed strip on its inboard face; matching driver-side console bolster |
| Cockpit wrap | B13, B38, B37 | Stitched welt ran down the driver side of the stack; a visor plank floated above the cluster | Welt runs from the driver door along the hood edge, across the dash lip above the stack and into the hoop; floating visor removed. "Cockpit wrap & grab handle" is one customisable part (hoop, brow, console bolsters) so a contrast interior reads like the photos |
| Stack top | B58, B21, B37 | Two vents with the hazard between | One wide vent across the left, PASS AIR BAG lamp and hazard in a pod on the right |
| Climate block | B58, B21 | Buttons as five-over-three | Two rows of six split by a chrome Y (AUTO, A/C, face / face+feet, defrost, SYNC; seat, feet, feet+defrost / rear defrost, recirc, seat) |
| Console | B37, B44, B38 | Plate centred with open cupholders | Brushed plate on the driver half carrying the shifter, drive-mode dial and EPB; long dark storage lid on the passenger half; small switch square front right; wider armrest that the bolsters run into |
| Steering wheel | B21, B04, B17 | Two flat arm plates and a separate stem; pods buried; small airbag | One silver V frame: arms from 9 and 3 o'clock sweep down around the airbag into the lower spoke; pods proud of the frame; larger airbag shield |
| Registry | | Parts list showed a glovebox and console side accents that no longer exist | Removed; console plate defaults to brushed aluminium; new "Console storage lid" part |

## Refinement pass (cluster, grab wing, raised keys), checked side by side with B41 / B58 / B13 / B21
| Area | Photo evidence | Change made |
|------|----------------|-------------|
| Gauge cluster | B41, B21, B13 | Binnacle rebuilt as one moulding with three openings: D-shaped side pods and the centre display, each a short tunnel. Left pod is the 0-200 mph speedometer whose arc wraps the outer edge with its needle pivoting beside the display; right pod carries fuel (1 / ½ / 0) above, coolant (260 / 220 / 100 °F) below and the CORVETTE script. Centre display themes: Tour (round tach with bright ring, redline, crossed flags, gear indicator), Track (shift dots, rising tach band, timers, gauge bars, tyre pressures, matching B41), Sport, and two concepts |
| Grab handle | B13, B21, B37, B16 | Brushed wing angled ~45 degrees off the stack's passenger edge, narrow at the top and widening downward, with a teardrop grab slot cut through it; the leather roll runs along its outer edge and turns rearward into the console bolster |
| Control panel | B58, B21 | Every key is a raised 3 mm cap with its label on the cap top; round MENU key; a 3D chrome Y between the climate halves; temperature knob face reads LO inside a blue-to-red ring, fan knob shows the fan |
| Driver dash | B21 | Driver outer vent and trim panel moved outboard so they clear the speedometer pod |

Fixes found while checking: two boolean cutters were inside out (one listed clockwise, one extruded with a negative
depth), so the slot and pod openings were not cut; knob labels were mis-oriented because revolved parts carry a node
rotation. All three now verified in captures.

## Passenger bar and detail pass (B38 / B13 / B49 / B41 / B44)
| Area | What was wrong | Change made |
|------|----------------|-------------|
| Passenger bar | A thin round tube with lumps at the bend, lying on top of the console like a pipe | One wide flat-faced leather band (46 x 26 mm) tucked over the brushed wing's outer edge, a single smooth bend at the foot (Bezier, evenly resampled), then a tall padded console side wall (300 mm deep) that runs into the armrest. The section changes continuously, so there are no seams. The wall continues forward under the stack to the dash lower on both sides, so the wrap colour covers the console sides as in B38 / B49 |
| Cockpit brow | Thin cord | Flat-faced rolled edge (22 x 14 mm) over the hood and the stack top, ending in the band |
| Gauge figures | Fuel and coolant numbers small; speedometer figures crowded; "0" hidden by the needle | Both side dials enlarged to the pod edge; speedometer spans 210 degrees like B41; condensed bold italic figures at the photo size; "0" beside the resting needle; fuel needle clear of "½" |
| CORVETTE script | Plain italic text | Wide, thin-stroked, forward-slanted logotype spread to a fixed width |
| Leather | About 1 cm grain cells with strong relief: read as hammered metal up close | About 1-2 mm grain (72 cells per tile, 9 tiles per metre) with softer relief; finer grain under the seat perforations |

Checked with a colour-per-object render at the band's bend: the subdivided band pulled in slightly and exposed the
lower wall's end; the wall is now subdivided and inset 2 mm.

Follow-up on the bar (B38 / B49):

| Area | What was wrong | Change made |
|------|----------------|-------------|
| Bend | The section grew into the tall console wall inside the bend and folded over itself | The section only grows once the path has left the bend |
| Console side under the stack | Faces were inside out, so the carpet showed through as dark triangles; it bulged outboard under the bend and left a vertical crease; it was in the wrap colour | Winding fixed (checked with horizontal ray casts: outer faces now point out); flush with the band's console wall, so the band's loop stands off it as in B49; dark console trim (part of "Console body") as in B38 |
| Wall bottoms | A fixed depth: the toe board and tunnel poked through near the front | The bottom of every console side wall follows the carpet height (tunnel hump plus toe board) and sits 8 mm into it |
| Driver console bolster | Inside out (mirrored frame) | Winding reversed |

Second follow-up on the bar (owner photo of the slot / B38):

| Area | What was wrong | Change made |
|------|----------------|-------------|
| Band line | The band sat about 0.23 m out at the stack but 0.146 m on the console, so it swerved inward at the foot and looked like a separate loop coming off the stack | The band keeps one x (about 0.20 m, measured from B38) from the stack's foot along the whole console into the armrest corner |
| Fin | Angled 45 degrees outboard, ending above the bend with a gap under it | Stands mostly rearward off the stack edge, facing the driver, and follows the band through the bend so its foot lies on the console top; the passenger-facing back is leather in the wrap colour (the red seen through the slot) |
| Console and armrest | Passenger edge at 0.155 m: too narrow to meet the band | Passenger side widened to 0.195 m with the top kept flat out under the band (no trench); armrest widened on that side; storage lid moved out with it |
| Band width on the console | Grew to about twice its stack width right after the bend (a visible shoulder) | Same thickness all the way, so it reads as one even strip from above |

## Passenger dash and vents (B37 / B38 / B60 / B66 / B58)

| Area | What was wrong | Change made |
|------|----------------|-------------|
| Passenger pad | A thin flat strip laid on the dash face, starting 5 cm short of the grab band | One sculpted pad from behind the band to the door: starts at the crease where the black dash top ends, stands proud with its face tilted up toward the occupant, rolls under into a shelf over the dark knee area, and eases into the dash at the door end |
| Vents | Housings with no back (the pad showed through between the louvres as red wedges); the outer vent crowded the door | Openings cut through the pad, each with a dark lined pocket, four tipped louvres and a slider, and a bezel standing 1.5 mm proud |
| Inner vent | A plain rectangle | A rounded trapezoid (about 96 x 60 mm) whose stack-side edge leans toward the door, as in B37 / B66 / B58 |
| Outer vent | Switches under the vent | A taller rounded square (78 x 104 mm) with the louvres in the top and the two seat switches, with light indicators, on a dark plate inside the bottom of the same bezel |
| Vent bezels | Dark grey by default | Bright satin silver as in the photos (the old default is migrated) |
| Colour of cut parts | Parts with a boolean cut load as a group of meshes; their component id was on the group only, so colour changes never reached them (also the fin's leather back) | The loader falls back to the parent's component id |

Verdict: the cockpit now matches the C7 photos in layout, proportion and the signature elements (Y-spoke wheel,
hooded three-tunnel cluster, driver-angled stack with grab fin, long aluminium console plate, GT seats with
headrest slot, aluminium door handles). Surface-level sculpting and stitching detail remain approximations.

## Stack top (B58 / B21 / B36 / B56)

| Area | What was wrong | Change made |
|------|----------------|-------------|
| Brow over the stack | Ran about 2 cm too low, straight across the vent | Runs along the top edge of the yawed stack face, just above the opening, then down into the passenger band |
| Vent and pod | A brushed rectangle with a separate gloss pod, crammed against the top edge | One long opening cut into the stack: tall and round at the driver end, narrowing toward the passenger end under the brow. Louvres with a chrome slider fill the left part; the PASS AIR BAG lamp module and the hazard button sit in the narrow right part. The walls are lined, with a dark gloss lip (no bright bezel), and every point follows the curved stack face |
| Screen surround | 126 mm tall, leaving no room under the opening | 118 mm tall (the 8-inch screen is unchanged), centred 3 mm lower |

