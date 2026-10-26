# PROGRESS — C7 Interior Studio

Living checklist. Survives interruptions; update at every stage boundary.

## Decisions (2026-10-26, from Tyler)
- 2019 Stingray Coupe 3LT, GT seats, 8-speed automatic, Jet Black; Stingray only.
- No money. Free references only; Tyler will supply photos if I cannot find enough (I cannot: network blocks all photo hosts, see docs/REFERENCES.md).
- Geometry built from scratch in Blender scripts, honestly labeled as a recreation, not a scan.
- Logos: labeled development placeholders, swappable.
- Project now lives in its own public repo `tylerrini85-cyber/c7-interior-studio` (claude-text is private, so Pages could not serve it from there).
- Hosting: GitHub Pages static build. Personal use. Local IndexedDB projects, no accounts.
- Targets: desktop Chrome/Safari, iOS Safari, Android Chrome. Name: **C7 Interior Studio**.
- Concept electronics labeled; free headrest text with a basic filter. Self-assessment first, Tyler reviews final.

## Environment facts
- Node 22, npm OK. Blender 4.0.2 headless installed via apt (+ python3-numpy); glTF export verified.
- No GPU: Cycles/Workbench CPU renders for checks; Playwright Chromium software WebGL for e2e.
- Network: only npm/PyPI/GitHub/ubuntu mirror reachable. WebSearch works (text only); WebFetch blocked for most hosts.

## Stage status
- [x] Stage 1 Research & feasibility — docs/REFERENCES.md, docs/ARCHITECTURE.md, dependencies installed
- [~] Stage 2 Cockpit geometry + materials — Blender pipeline (`tools/blender`) builds cabin, dash, cluster, column, wheel (+3 variants), console (+2 shifter variants), GT seats (+2 variants), doors; GLB 2.7 MB / 75k tris. Refinement list below.
- [x] Stage 3 Camera — driver/passenger POV, drag look, WASD/arrows, wheel zoom, joystick, free roam with collision, inspect mode, focus, reset, eye height, FOV
- [x] Stage 4 Customization core — registry (70 components), raycast selection + outline, parts browser synced, inspector, material engine, variant swapping
- [x] Stage 5 Materials/lighting — procedural leather/perforated/alcantara/carbon twill/forged/brushed metal/carpet maps, stitching overlays, 10 RGB zones with real point lights + 8 modes, starlight headliner (5 patterns, twinkle, shooting), 4 environments, gauge/infotainment themes
- [x] Stage 6 Persistence — IndexedDB garage, autosave + indicator, thumbnails, export/import, rename/duplicate/delete, undo/redo (150 steps), factory reset
- [x] Stage 7 UI — landing, garage, new project, settings (quality modes), help; desktop panels; mobile sheets/fabs/joystick
- [x] Stage 8 Extras — 9 presets, 6-theme randomizer with compatibility rules, factory compare + side-by-side export, screenshot PNG, showroom mode
- [x] Stage 9 Testing — 16 unit tests, 20/20 e2e steps, ten-view captures; see docs/TEST-RESULTS.md and docs/VISUAL-ASSESSMENT.md
- [x] Stage 10 Delivery — README, ASSET-LICENSES, KNOWN-LIMITATIONS, TEST-RESULTS, Pages workflow (needs Pages enabled once)

## Open items
- Stage 2 visual approval gate stays open until Tyler reviews against photos (docs/REFERENCES.md lists the photos wanted).

## Geometry refinement list (Stage 2 follow-ups)
- Done this pass: flatter airbag shield, backrest taper + shoulder wings, pleated inserts, door armrest shelf + rolled
  top bolster + pull bridge with opening, stitched cockpit-wrap welt, adaptive pixel ratio + fps readout.
- Still open (needs photos to do well): exact seat sculpt and seam paths, button graphics on the wheel pods, vent vane
  thickness, cluster bezel lip, door moulding detail.

## Known defects / limitations
- See docs/KNOWN-LIMITATIONS.md.
- Environment facts: three's GLTFLoader strips dots from node names, so component ids are read from glTF extras (`ct_component`).

## Missing assets
- Reference photos (requested from Tyler, docs/REFERENCES.md bottom).
