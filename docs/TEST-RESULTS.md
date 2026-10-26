# Test results (2026-10-26)

Environment: cloud Linux container, 4 CPU, no GPU. Browser tests use the preinstalled Chromium with SwiftShader
(software WebGL), so frame rates there say nothing about real hardware. Automated results are listed as run;
items that still need a human are marked explicitly.

## Automated

| Suite | Command | Result |
|-------|---------|--------|
| Unit (vitest, jsdom) | `npm test` | **16/16 passed** — registry integrity and factory colors; store create/undo/redo/transient coalescing/linked seats/part isolation/factory reset/variants; presets and randomizer stay within component capabilities for all 6 themes × 5 seeds; schema migration; export/import round trip |
| TypeScript | `tsc -b` (part of `npm run build`) | passes, strict mode |
| Production build | `npm run build` | passes (index 354 kB, three/r3f chunk 1.3 MB gzip 429 kB, models 2.7 MB + variants) |
| End-to-end walkthrough | `npm run test:e2e` (tests/e2e.cjs, production preview, quality=mobile) | **20/20 steps passed, no console or page errors** |

End-to-end steps covered: landing menu · create project A (Adrenaline Red, night) · select from parts list and change
material (mesh material verified) · geometry variant swap loads the flat-bottom wheel GLB and unregisters factory
nodes · click-to-select through raycast · undo/redo · all RGB zones + starlight (point cloud verified) · preset ·
environment switch · autosave status · create project B with different settings · reload, both projects present, A and
B unchanged · thumbnail captured · export/import round trip · duplicate/rename/delete with confirmation · PNG
screenshot download · before/after compare shows factory materials and restores the design · factory reset and random
generator · seat buttons, free-roam movement (WASD switches to free mode) and reset · mobile layout with bottom sheet,
inspector and joystick.

Visual capture scripts: `tests/render-views.cjs` produced `docs/renders-web/01..10` (see `docs/VISUAL-ASSESSMENT.md`).
Blender check renders: `docs/renders/`.

## Defects found and fixed during testing
- three's GLTFLoader strips dots from node names → component ids now come from glTF extras.
- A `useFrame` render priority disabled automatic rendering (black canvas).
- Screen textures used the UV box of side faces → only occupant-facing faces define the box.
- RGB strips showed as dim lines when off → hidden when off; point-light intensity reduced.
- Preset trim matcher matched "stee**ring**" → segment-based matcher.
- Thumbnail capture re-triggered itself on every thumbnail save → keyed on `updatedAt` only.
- Mesh-registry listeners fired synchronously per mesh (254×) → batched per microtask; selection diffing; stable hide-prefix deps.
- Factory-compare selector returned a fresh object per read (React snapshot loop) → memoized.
- Joystick did not appear on narrow layouts unless toggled → automatic on mobile/touch.

## Still requires a human
- Visual accuracy against real C7 photographs (all ten views) — see VISUAL-ASSESSMENT.md.
- Frame rate on real desktop GPUs and phones (iPhone Safari, Android Chrome) for each quality preset.
- Touch feel of the joystick and look-drag on a real device.
- GitHub Pages deployment (workflow written; Pages must be enabled in the repository settings).
