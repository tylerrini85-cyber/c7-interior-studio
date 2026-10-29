# Clearance check: builds seats, console, dashboard and cabin, then reports any seat vertex inside a console part
# (console body, armrest, bands) and any console vertex inside a seat. Run headless:
#   xvfb-run -a blender -b --python tools/blender/check_clearance.py   (prints DONE 0 / DONE2 0 when clear)
import os, sys, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
lib.reset_scene(); lib.ensure_collection('Cockpit')
for name in ('seats', 'console', 'dashboard', 'cabin'):
    importlib.import_module(f'parts.{name}').build()
dg = bpy.context.evaluated_depsgraph_get()
def world_mesh(o):
    e = o.evaluated_get(dg); me = e.to_mesh()
    vs = [o.matrix_world @ v.co for v in me.vertices]; fs = [tuple(p.vertices) for p in me.polygons]
    e.to_mesh_clear(); return vs, fs
solids = [o for o in bpy.data.objects if o.type == 'MESH' and not o.get('ct_cutter') and (o.name.startswith('console.') or o.name in ('dash.grab', 'dash.grab.lower', 'console.bolster.driver'))]
trees = {}
for o in solids:
    vs, fs = world_mesh(o)
    if fs: trees[o.name] = BVHTree.FromPolygons(vs, fs)
def inside(tree, p):
    hit = 0
    for d in (Vector((1, 0.013, 0.007)), Vector((-0.011, 1, 0.017)), Vector((0.01, -0.02, -1))):
        n = 0; q = p.copy()
        for _ in range(40):
            loc, nrm, idx, dist = tree.ray_cast(q, d)
            if loc is None: break
            n += 1; q = loc + d * 1e-5
        hit += n % 2
    return hit >= 2
res = {}
for o in bpy.data.objects:
    if o.type != 'MESH' or not o.name.startswith('seats.'): continue
    vs, fs = world_mesh(o)
    for p in vs:
        if abs(p.x) > 0.25 or p.y > 0.4 or p.y < -0.6: continue
        for nm, t in trees.items():
            if inside(t, p):
                k = (o.name, nm); r = res.setdefault(k, [0, 9, -9, 9, -9, 9, -9])
                r[0] += 1; r[1] = min(r[1], p.y); r[2] = max(r[2], p.y); r[3] = min(r[3], p.z); r[4] = max(r[4], p.z); r[5] = min(r[5], abs(p.x)); r[6] = max(r[6], abs(p.x))
for (s, c), r in sorted(res.items()):
    print(f'CLASH {s:40s} in {c:28s} n={r[0]:5d} y[{r[1]:.3f},{r[2]:.3f}] z[{r[3]:.3f},{r[4]:.3f}] |x|[{r[5]:.3f},{r[6]:.3f}]')
print('DONE', len(res))
# reverse: console-part vertices inside seat meshes
seat_trees = {}
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith('seats.') and ('bolsters' in o.name or 'center' in o.name or 'shell' in o.name):
        vs, fs = world_mesh(o)
        if fs: seat_trees[o.name] = BVHTree.FromPolygons(vs, fs)
res2 = {}
for o in solids:
    vs, fs = world_mesh(o)
    for p in vs:
        if p.y > 0.35 or p.y < -0.6: continue
        for nm, t in seat_trees.items():
            if inside(t, p):
                k = (o.name, nm); r = res2.setdefault(k, [0, 9, -9, 9, -9, 9, -9])
                r[0] += 1; r[1] = min(r[1], p.y); r[2] = max(r[2], p.y); r[3] = min(r[3], p.z); r[4] = max(r[4], p.z); r[5] = min(r[5], abs(p.x)); r[6] = max(r[6], abs(p.x))
for (s_, c), r in sorted(res2.items()):
    print(f'REV {s_:28s} in {c:40s} n={r[0]:5d} y[{r[1]:.3f},{r[2]:.3f}] z[{r[3]:.3f},{r[4]:.3f}] |x|[{r[5]:.3f},{r[6]:.3f}]')
print('DONE2', len(res2))
# plan view: along the seat cushions, how far the console parts reach outboard versus where the cushion's top starts
print('PLAN  y      console|x|max   cushion-top|x|min (z>0.33)   overlap')
cons = {}
for o in solids:
    vs, fs = world_mesh(o)
    for p in vs:
        if -0.26 <= p.y <= 0.26:
            k = round(p.y * 20) / 20
            cons[k] = max(cons.get(k, 0.0), abs(p.x))
seat = {}
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith('seats.') and '.base.' in o.name:
        vs, fs = world_mesh(o)
        for p in vs:
            if -0.26 <= p.y <= 0.26 and p.z > 0.33:
                k = round(p.y * 20) / 20
                seat[k] = min(seat.get(k, 9.0), abs(p.x))
worst = 0.0
for k in sorted(cons):
    if k in seat:
        ov = cons[k] - seat[k]
        worst = max(worst, ov)
        print(f'PLAN {k:+.2f}   {cons[k]:.3f}          {seat[k]:.3f}                     {ov * 1000:+.0f} mm')
print(f'PLAN worst overlap {worst * 1000:.0f} mm')
