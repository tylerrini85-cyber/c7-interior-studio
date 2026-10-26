# Known limitations and open items

## Geometry accuracy (highest priority to improve)
- The cockpit is a scripted recreation. Proportions come from published figures (headroom, legroom, shoulder/hip room,
  steering wheel diameter, 8-inch screens) and from descriptions of the C7 layout; every other dimension is estimated.
  Items flagged APPROX in `docs/REFERENCES.md` need checking against photographs (requested from Tyler).
- Seats: the GT seat has the correct overall architecture (sculpted base, bolstered back with shoulder wings, pleated
  inserts, integrated headrest, back shell) but the surface sculpting is still simplified compared with the real seat.
- Steering wheel: correct 14.1 in diameter, three spokes, thumb rests, paddles and airbag shield, but the button pods
  and the exact spoke profiles are simplified. The emblem is a placeholder badge.
- Dashboard: driver hood, angled center stack, passenger grab handle, trim band, glovebox and the stitched cockpit-wrap
  welt are present; the welt path is approximated. Door panels have the armrest shelf, pull bridge with opening, rolled
  top bolster, switch panel, speaker and pocket, but remain simpler than the real moulding.
- No exterior body; what you see through the glass is a procedural environment.

## Rendering
- Software WebGL (as used by the headless test run) is slow; real GPUs are the target. Ultra/High enable ambient
  occlusion and shadows; Balanced/Mobile reduce or disable them. An adaptive controller lowers the pixel ratio when the
  frame rate drops below ~28 fps and restores it above ~55 fps; the current fps shows under the camera bar's view options.
- Stitching is a tiled overlay texture aligned to the mesh UVs (meters), so seams follow panel UV flow rather than
  modeled seam paths. Diamond/hex quilting looks best on seat inserts and armrests.
- Transmission glass is replaced by a tinted transparent material for performance.

## Platform
- Projects live in the browser (IndexedDB). Clearing site data deletes them; export JSON backups from the Garage.
- Custom text uses a small profanity filter; it is not a complete moderation system.
- The GitHub Pages workflow deploys from the claude-text repository's default branch; Pages must be enabled once.

## Not implemented
- Convertible body, Grand Sport/Z06 interiors, manual-transmission console geometry beyond the shifter.
- Cloud accounts / sync (architecture allows adding it).
