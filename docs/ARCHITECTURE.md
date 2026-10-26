# Architecture — C7 Interior Studio

## Stack
- React 19 + TypeScript 6 + Vite 8
- Three.js 0.186, @react-three/fiber 9, @react-three/drei 10
- Zustand 5 (+ immer) for state; idb 8 for IndexedDB persistence
- Vitest for unit tests, Playwright for end-to-end and render checks
- Blender 4.0 (headless, scripted in Python) builds all cockpit geometry and exports glTF/GLB
- Procedural textures generated with Python (numpy + Pillow) at build time

## Systems (one folder each under `src/`)
| # | System | Folder | Notes |
|---|--------|--------|-------|
| 1 | App shell and navigation | `app/` | Landing menu, routes (menu, garage, studio, settings, help) |
| 2 | Project management | `project/` | schema, migrations, create/duplicate/rename/delete |
| 3 | Scene renderer | `scene/` | Canvas, environment modes, tone mapping, quality presets |
| 4 | Asset loading | `assets/` | staged GLB + texture loading with progress and retry |
| 5 | Camera control | `camera/` | POV rig, look/orbit, WASD, joystick, collision, inspection |
| 6 | Part selection | `selection/` | raycast picking, hover and selected highlight, sync with menu |
| 7 | Component registry | `registry/` | stable ids, categories, allowed properties, variant slots |
| 8 | Customization state | `state/` | single store: project doc + UI state; selectors |
| 9 | Material system | `materials/` | presets (carbon, leather, alcantara, metals, plastics), param → MeshPhysicalMaterial |
| 10 | Geometry replacement | `variants/` | mesh swapping with attachment points and compatibility rules |
| 11 | Lighting | `lighting/` | RGB zones (emissive + real point/rect lights), animation modes, starlight headliner |
| 12 | Undo/redo | `history/` | command stack over project patches |
| 13 | Persistence | `persistence/` | IndexedDB repo, autosave, export/import, thumbnails |
| 14 | Screenshot | `capture/` | preserveDrawingBuffer-free capture via render-to-target |
| 15 | Quality/performance | `quality/` | Ultra/High/Balanced/Mobile, DPR, shadows, adaptive |

## Component ids
Dot-separated, stable, used by GLB node names, registry, project files and UI:
`steering.rim.upper`, `steering.rim.lower`, `steering.grip.left`, `steering.grip.right`, `steering.spokes`, `steering.hub`,
`cluster.bezel`, `cluster.screen`, `dash.upper`, `dash.lower.driver`, `dash.lower.passenger`, `dash.trim.driver`,
`dash.trim.passenger`, `dash.vents`, `dash.grab`, `console.main`, `console.trim`, `console.shifter`, `console.armrest`,
`console.screen`, `seats.driver.*`, `seats.passenger.*`, `doors.driver.*`, `doors.passenger.*`, `roof.headliner`,
`roof.panel`, `pillars`, `floor.carpet`, `floor.mats`, `pedals`, `lighting.zone.<name>`, `lighting.starlight`.

## Project document (schema v1)
```ts
interface ProjectDoc {
  schemaVersion: 1;
  id: string; name: string; createdAt: string; updatedAt: string;
  base: { year: 2019; trim: '3LT'; seats: 'GT'; transmission: 'A8'; body: 'coupe'; factoryColor: FactoryColorId };
  parts: Record<ComponentId, PartConfig>;      // material, colors, stitching, finish, variant
  lighting: { master: LightingMaster; zones: Record<ZoneId, ZoneConfig>; starlight: StarlightConfig };
  environment: EnvironmentId; camera?: CameraPrefs; thumbnail?: string;
}
```
Material and geometry are separate operations: `PartConfig.variant` swaps meshes (geometry replacement system),
`PartConfig.material` + colors drive the material engine. Undo/redo stores inverse patches of `ProjectDoc`.

## Asset pipeline
`tools/blender/build.py` → `public/models/c7-cockpit.glb` (factory cockpit) and `public/models/variants/*.glb`
(alternate steering wheels, seats, shifters). `tools/textures/gen.py` → `public/textures/*.png`
(leather normal, perforation, carbon twill, forged carbon, alcantara, brushed metal). Blender's Workbench/Cycles CPU
renders in `tools/blender/render.py` produce `docs/renders/*.png` for self-assessment.
