"""Mesh-building helpers for the C7 Interior Studio Blender pipeline.

Coordinate frame (Blender): +X = passenger side (right of driver), +Y = forward (toward windshield), +Z = up.
Floor at Z=0. Units are meters. The glTF exporter converts to Y-up.
"""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

# ---------------------------------------------------------------------------
# scene / object utilities
# ---------------------------------------------------------------------------

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    return scene


def ensure_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def new_object(name, mesh, collection='Cockpit', parent=None):
    obj = bpy.data.objects.new(name, mesh)
    ensure_collection(collection).objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def mesh_from_pydata(name, verts, faces, uvs=None, smooth=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if uvs is not None:
        uv_layer = me.uv_layers.new(name='UVMap')
        # uvs: list per face of list of (u,v) per loop
        li = 0
        for fi, poly in enumerate(me.polygons):
            face_uv = uvs[fi]
            for k in range(poly.loop_total):
                uv_layer.data[poly.loop_start + k].uv = face_uv[k]
    return me


# ---------------------------------------------------------------------------
# 2D profile generators (return list of Vector((x, y)) in a local plane)
# ---------------------------------------------------------------------------

def circle2d(r, n=32, start=0.0):
    return [Vector((r * math.cos(start + 2 * math.pi * i / n), r * math.sin(start + 2 * math.pi * i / n))) for i in range(n)]


def superellipse2d(a, b, e=2.5, n=48):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        x = math.copysign(abs(c) ** (2 / e), c) * a
        y = math.copysign(abs(s) ** (2 / e), s) * b
        pts.append(Vector((x, y)))
    return pts


def rounded_rect2d(w, h, r, n_corner=6, offset=(0.0, 0.0)):
    """Closed rounded rectangle centred at origin, counter-clockwise, starting bottom-right corner."""
    r = min(r, w / 2, h / 2)
    hw, hh = w / 2, h / 2
    pts = []
    corners = [(hw - r, -hh + r, -math.pi / 2), (hw - r, hh - r, 0.0), (-hw + r, hh - r, math.pi / 2), (-hw + r, -hh + r, math.pi)]
    for cx, cy, a0 in corners:
        for i in range(n_corner + 1):
            a = a0 + (math.pi / 2) * i / n_corner
            pts.append(Vector((cx + r * math.cos(a) + offset[0], cy + r * math.sin(a) + offset[1])))
    return pts


def resample_closed(points, n):
    """Resample a closed polyline to n points by arc length."""
    pts = [Vector(p) for p in points]
    segs = [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    lens = [(b - a).length for a, b in segs]
    total = sum(lens)
    out = []
    for k in range(n):
        d = total * k / n
        acc = 0.0
        for (a, b), L in zip(segs, lens):
            if acc + L >= d or (a, b) == segs[-1]:
                t = 0.0 if L == 0 else (d - acc) / L
                out.append(a.lerp(b, max(0.0, min(1.0, t))))
                break
            acc += L
    return out


def resample_open(points, n):
    pts = [Vector(p) for p in points]
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    lens = [(b - a).length for a, b in segs]
    total = sum(lens)
    out = []
    for k in range(n):
        d = total * k / (n - 1)
        acc = 0.0
        for idx, ((a, b), L) in enumerate(zip(segs, lens)):
            if acc + L >= d - 1e-9 or idx == len(segs) - 1:
                t = 0.0 if L == 0 else (d - acc) / L
                out.append(a.lerp(b, max(0.0, min(1.0, t))))
                break
            acc += L
    return out


def bezier2d(p0, p1, p2, p3, n=12):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        p = (u ** 3) * Vector(p0) + 3 * (u ** 2) * t * Vector(p1) + 3 * u * (t ** 2) * Vector(p2) + (t ** 3) * Vector(p3)
        out.append(p)
    return out


def spline_through(points, n_per_seg=6, closed=False, tension=0.5):
    """Catmull-Rom spline through points (2D or 3D Vectors)."""
    pts = [Vector(p) for p in points]
    m = len(pts)
    out = []
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = pts[(i - 1) % m] if closed else pts[max(i - 1, 0)]
        p1 = pts[i]
        p2 = pts[(i + 1) % m]
        p3 = pts[(i + 2) % m] if closed else pts[min(i + 2, m - 1)]
        for k in range(n_per_seg):
            t = k / n_per_seg
            t2, t3 = t * t, t * t * t
            a = -tension * t3 + 2 * tension * t2 - tension * t
            b = (2 - tension) * t3 + (tension - 3) * t2 + 1
            c = (tension - 2) * t3 + (3 - 2 * tension) * t2 + tension * t
            d = tension * t3 - tension * t2
            out.append(a * p0 + b * p1 + c * p2 + d * p3)
    if not closed:
        out.append(pts[-1])
    return out


# ---------------------------------------------------------------------------
# placing 2D profiles in 3D
# ---------------------------------------------------------------------------

def place_profile(profile2d, origin, u_axis, v_axis, scale=(1.0, 1.0)):
    o = Vector(origin)
    u = Vector(u_axis).normalized()
    v = Vector(v_axis).normalized()
    return [o + u * (p.x * scale[0]) + v * (p.y * scale[1]) for p in profile2d]


def frame_along_path(path, up_hint=Vector((0, 0, 1))):
    """Return list of (origin, tangent, normal, binormal) along a 3D polyline using parallel transport."""
    pts = [Vector(p) for p in path]
    n = len(pts)
    frames = []
    prev_normal = None
    for i in range(n):
        if i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == n - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = ((pts[i + 1] - pts[i]).normalized() + (pts[i] - pts[i - 1]).normalized()).normalized()
        if prev_normal is None:
            hint = Vector(up_hint)
            if abs(hint.dot(t)) > 0.99:
                hint = Vector((1, 0, 0))
            nrm = (hint - t * hint.dot(t)).normalized()
        else:
            nrm = (prev_normal - t * prev_normal.dot(t)).normalized()
        b = t.cross(nrm).normalized()
        frames.append((pts[i], t, nrm, b))
        prev_normal = nrm
    return frames


# ---------------------------------------------------------------------------
# surface builders
# ---------------------------------------------------------------------------

def loft(rings, close_u=True, cap_start=False, cap_end=False, uv_scale=1.0, flip=False):
    """Build (verts, faces, uvs) connecting successive rings of equal length.
    UVs: u = arc length around the ring, v = cumulative distance between rings (meters * uv_scale)."""
    n = len(rings[0])
    verts = []
    for r in rings:
        assert len(r) == n, 'all rings must have the same point count'
        verts.extend(r)
    faces, uvs = [], []
    # per-ring arc-length u coordinate
    u_coords = []
    for r in rings:
        acc = [0.0]
        for i in range(1, n + (1 if close_u else 0)):
            acc.append(acc[-1] + (Vector(r[i % n]) - Vector(r[i - 1])).length)
        u_coords.append(acc)
    v_coords = [0.0]
    for k in range(1, len(rings)):
        d = sum((Vector(rings[k][i]) - Vector(rings[k - 1][i])).length for i in range(n)) / n
        v_coords.append(v_coords[-1] + d)
    m = n if close_u else n - 1
    for k in range(len(rings) - 1):
        for i in range(m):
            a = k * n + i
            b = k * n + (i + 1) % n
            c = (k + 1) * n + (i + 1) % n
            d = (k + 1) * n + i
            f = (a, d, c, b) if flip else (a, b, c, d)
            faces.append(f)
            ua, ub = u_coords[k][i], u_coords[k][i + 1]
            uc, ud = u_coords[k + 1][i + 1], u_coords[k + 1][i]
            va, vb = v_coords[k], v_coords[k + 1]
            quad_uv = [(ua * uv_scale, va * uv_scale), (ub * uv_scale, va * uv_scale), (uc * uv_scale, vb * uv_scale), (ud * uv_scale, vb * uv_scale)]
            if flip:
                quad_uv = [quad_uv[0], quad_uv[3], quad_uv[2], quad_uv[1]]
            uvs.append(quad_uv)
    def cap_uvs(ring):
        pts = [Vector(p) for p in ring]
        c = sum(pts, Vector((0, 0, 0))) / len(pts)
        # plane basis from the ring: u = longest axis of the ring in its plane
        nrm = Vector((0, 0, 0))
        for i in range(len(pts)):
            nrm += (pts[i] - c).cross(pts[(i + 1) % len(pts)] - c)
        if nrm.length < 1e-12:
            nrm = Vector((0, 0, 1))
        nrm.normalize()
        ref = Vector((1, 0, 0)) if abs(nrm.x) < 0.9 else Vector((0, 1, 0))
        u = (ref - nrm * ref.dot(nrm)).normalized()
        v = nrm.cross(u).normalized()
        return [((p - c).dot(u) * uv_scale, (p - c).dot(v) * uv_scale) for p in pts]
    if cap_start:
        f = tuple(range(n))
        order = list(reversed(f)) if not flip else list(f)
        faces.append(tuple(order))
        cu = cap_uvs(rings[0])
        uvs.append([cu[i] for i in order])
    if cap_end:
        base = (len(rings) - 1) * n
        order = list(range(n)) if not flip else list(reversed(range(n)))
        faces.append(tuple(base + i for i in order))
        cu = cap_uvs(rings[-1])
        uvs.append([cu[i] for i in order])
    return verts, faces, uvs


def loft_object(name, rings, close_u=True, cap_start=False, cap_end=False, material=None, collection='Cockpit', subsurf=0, uv_scale=1.0, flip=False, crease=0.0):
    verts, faces, uvs = loft(rings, close_u, cap_start, cap_end, uv_scale, flip)
    me = mesh_from_pydata(name, verts, faces, uvs)
    obj = new_object(name, me, collection)
    if material is not None:
        set_material(obj, material)
    if subsurf:
        add_subsurf(obj, subsurf)
    return obj


def sweep_tube(name, path, radius, n=16, radius_fn=None, closed_path=False, cap=True, material=None, collection='Cockpit', up_hint=Vector((0, 0, 1)), subsurf=0, uv_scale=1.0):
    """Sweep a circle (radius may vary with radius_fn(t) in [0,1]) along a 3D path."""
    pts = [Vector(p) for p in path]
    if closed_path:
        pts = pts + [pts[0]]
    frames = frame_along_path(pts, up_hint)
    rings = []
    for i, (o, t, nrm, b) in enumerate(frames):
        s = i / (len(frames) - 1)
        r = radius if radius_fn is None else radius_fn(s)
        if isinstance(r, tuple):
            ring = [o + nrm * (r[0] * math.cos(2 * math.pi * k / n)) + b * (r[1] * math.sin(2 * math.pi * k / n)) for k in range(n)]
        else:
            ring = [o + nrm * (r * math.cos(2 * math.pi * k / n)) + b * (r * math.sin(2 * math.pi * k / n)) for k in range(n)]
        rings.append(ring)
    if closed_path:
        rings[-1] = rings[0]
        verts, faces, uvs = loft(rings[:-1] + [rings[0]], True, False, False, uv_scale)
        # weld last ring onto first
        nn = len(rings[0])
        total = len(rings) - 1
        remap = lambda idx: idx if idx < total * nn else idx - total * nn
        faces = [tuple(remap(i) for i in f) for f in faces]
        verts = verts[:total * nn]
        me = mesh_from_pydata(name, verts, faces, uvs)
    else:
        verts, faces, uvs = loft(rings, True, cap, cap, uv_scale)
        me = mesh_from_pydata(name, verts, faces, uvs)
    obj = new_object(name, me, collection)
    if material is not None:
        set_material(obj, material)
    if subsurf:
        add_subsurf(obj, subsurf)
    return obj


def ribbon(name, pts, normals, width, thick, material=None, collection='Cockpit', uv_scale=1.0, bevel=0.0):
    """Sweep a flat rectangular strip (width across the surface, thick along the given surface normals) along a
    polyline. The wide face lies on the surface described by `normals`; the strip stands `thick` proud of it."""
    pts = [Vector(p) for p in pts]
    rings = []
    n_pts = len(pts)
    for i in range(n_pts):
        if i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == n_pts - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = ((pts[i + 1] - pts[i]).normalized() + (pts[i] - pts[i - 1]).normalized()).normalized()
        nn = Vector(normals[i]).normalized()
        nn = (nn - t * nn.dot(t)).normalized()
        b = t.cross(nn).normalized()
        o = pts[i]
        rings.append([o - b * (width / 2), o + b * (width / 2), o + b * (width / 2) + nn * thick, o - b * (width / 2) + nn * thick])
    obj = loft_object(name, rings, close_u=True, cap_start=True, cap_end=True, material=material, collection=collection, uv_scale=uv_scale)
    if bevel > 0:
        add_bevel(obj, bevel, 2)
    return obj


def extrude_profile(name, profile2d, origin, u_axis, v_axis, depth, material=None, collection='Cockpit', bevel=0.0, bevel_segments=3, subsurf=0, uv_scale=1.0, taper=1.0):
    """Extrude a closed 2D profile along the plane normal by depth. taper scales the far face."""
    u = Vector(u_axis).normalized(); v = Vector(v_axis).normalized(); nrm = u.cross(v).normalized()
    r0 = place_profile(profile2d, origin, u, v)
    r1 = place_profile(profile2d, Vector(origin) + nrm * depth, u, v, scale=(taper, taper))
    obj = loft_object(name, [r0, r1], True, True, True, material, collection, 0, uv_scale)
    if bevel > 0:
        add_bevel(obj, bevel, bevel_segments)
    if subsurf:
        add_subsurf(obj, subsurf)
    return obj


def revolve(name, profile_rz, segments=32, material=None, collection='Cockpit', axis='Z', origin=(0, 0, 0), direction=None, subsurf=0, cap=True):
    """Revolve an open (r, h) profile around an axis. profile_rz: list of (radius, height)."""
    rings = []
    for (r, h) in profile_rz:
        ring = []
        for k in range(segments):
            a = 2 * math.pi * k / segments
            ring.append(Vector((r * math.cos(a), r * math.sin(a), h)))
        rings.append(ring)
    verts, faces, uvs = loft(rings, True, cap, cap)
    me = mesh_from_pydata(name, verts, faces, uvs)
    obj = new_object(name, me, collection)
    if direction is not None:
        d = Vector(direction).normalized()
        q = Vector((0, 0, 1)).rotation_difference(d)
        obj.rotation_euler = q.to_euler()
    obj.location = Vector(origin)
    if material is not None:
        set_material(obj, material)
    if subsurf:
        add_subsurf(obj, subsurf)
    return obj


def box(name, size, center, material=None, collection='Cockpit', bevel=0.0, bevel_segments=4, subsurf=0, rotation=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me)
    bm.free()
    uv_layer = me.uv_layers.new(name='UVMap')
    me.update()
    obj = new_object(name, me, collection)
    from mathutils import Euler
    mw = Matrix.Translation(Vector(center)) @ Euler(rotation).to_matrix().to_4x4() @ Matrix.Diagonal((size[0], size[1], size[2], 1.0))
    me.transform(mw)
    cube_project_uv(obj)
    if material is not None:
        set_material(obj, material)
    if bevel > 0:
        add_bevel(obj, bevel, bevel_segments)
    if subsurf:
        add_subsurf(obj, subsurf)
    return obj


def cube_project_uv(obj, scale=1.0):
    me = obj.data
    uv = me.uv_layers.active.data
    for poly in me.polygons:
        n = poly.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            if ax == 0:
                uv[li].uv = (co.y * scale, co.z * scale)
            elif ax == 1:
                uv[li].uv = (co.x * scale, co.z * scale)
            else:
                uv[li].uv = (co.x * scale, co.y * scale)


def apply_transforms(obj):
    bpy.context.view_layer.update()
    mw = obj.matrix_world.copy()
    obj.data.transform(mw)
    obj.matrix_world = Matrix.Identity(4)


def mirror_x(obj, new_name=None):
    """Return a mirrored copy across the YZ plane (X -> -X) with corrected normals."""
    me = obj.data.copy()
    me.transform(Matrix.Scale(-1, 4, Vector((1, 0, 0))))
    me.flip_normals()
    new = bpy.data.objects.new(new_name or (obj.name + '_mirror'), me)
    for c in obj.users_collection:
        c.objects.link(new)
    new.matrix_world = obj.matrix_world.copy()
    for m in obj.modifiers:
        nm = new.modifiers.new(m.name, m.type)
        for prop in m.bl_rna.properties:
            if not prop.is_readonly and prop.identifier not in ('name', 'type'):
                try:
                    setattr(nm, prop.identifier, getattr(m, prop.identifier))
                except Exception:
                    pass
    return new


def join(objs, name):
    """Join objects into one mesh via bmesh (background-safe)."""
    bm = bmesh.new()
    dg = bpy.context.evaluated_depsgraph_get()
    mats = []
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        me.transform(o.matrix_world)
        # remap material indices
        offset = len(mats)
        for m in me.materials:
            if m not in mats:
                mats.append(m)
        tmp = bmesh.new()
        tmp.from_mesh(me)
        for f in tmp.faces:
            f.material_index = mats.index(me.materials[f.material_index]) if me.materials else 0
        tmp_me = bpy.data.meshes.new('tmp')
        tmp.to_mesh(tmp_me)
        bm.from_mesh(tmp_me)
        bpy.data.meshes.remove(tmp_me)
        tmp.free()
        ev.to_mesh_clear()
    out = bpy.data.meshes.new(name)
    bm.to_mesh(out)
    bm.free()
    for m in mats:
        out.materials.append(m)
    for p in out.polygons:
        p.use_smooth = True
    obj = new_object(name, out, objs[0].users_collection[0].name)
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)
    return obj


# ---------------------------------------------------------------------------
# modifiers
# ---------------------------------------------------------------------------

def add_subsurf(obj, levels=2, boundary_smooth='ALL'):
    m = obj.modifiers.new('Subdivision', 'SUBSURF')
    m.levels = levels
    m.render_levels = levels
    m.boundary_smooth = boundary_smooth
    return m


def add_bevel(obj, width, segments=3, angle_limit=math.radians(40), clamp=True):
    m = obj.modifiers.new('Bevel', 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = angle_limit
    m.use_clamp_overlap = clamp
    m.harden_normals = False
    return m


def add_solidify(obj, thickness, offset=-1.0):
    m = obj.modifiers.new('Solidify', 'SOLIDIFY')
    m.thickness = thickness
    m.offset = offset
    m.use_even_offset = True
    return m


def add_boolean(obj, cutter, op='DIFFERENCE', hide_cutter=True):
    m = obj.modifiers.new('Boolean', 'BOOLEAN')
    m.operation = op
    m.object = cutter
    m.solver = 'EXACT'
    if hide_cutter:
        cutter.hide_render = True
        cutter.hide_viewport = True
        cutter['ct_cutter'] = True
    return m


def add_mirror(obj, axis=0, merge=True):
    m = obj.modifiers.new('Mirror', 'MIRROR')
    m.use_axis = [axis == 0, axis == 1, axis == 2]
    m.use_mirror_merge = merge
    return m


def set_crease(obj, value=1.0, select=None):
    """Set edge crease on all edges (or a predicate on edge verts)."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    cl = bm.edges.layers.float.get('crease_edge') or bm.edges.layers.float.new('crease_edge')
    for e in bm.edges:
        if select is None or select(e.verts[0].co, e.verts[1].co):
            e[cl] = value
    bm.to_mesh(me)
    bm.free()


def shade_smooth(obj, auto_angle=math.radians(35)):
    for p in obj.data.polygons:
        p.use_smooth = True


# ---------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------

MATERIALS = {}

MATERIAL_DEFS = {
    # name: (base color rgba, roughness, metallic)
    'leather_black': ((0.025, 0.024, 0.024, 1), 0.55, 0.0),
    'leather_black_perf': ((0.025, 0.024, 0.024, 1), 0.6, 0.0),
    'suede_black': ((0.03, 0.03, 0.032, 1), 0.95, 0.0),
    'plastic_black': ((0.02, 0.02, 0.02, 1), 0.5, 0.0),
    'plastic_black_gloss': ((0.01, 0.01, 0.01, 1), 0.08, 0.0),
    'plastic_soft': ((0.03, 0.03, 0.03, 1), 0.7, 0.0),
    'metal_brushed': ((0.55, 0.56, 0.58, 1), 0.35, 1.0),
    'metal_satin_dark': ((0.25, 0.26, 0.28, 1), 0.4, 1.0),
    'chrome': ((0.9, 0.9, 0.9, 1), 0.05, 1.0),
    'carbon': ((0.05, 0.05, 0.055, 1), 0.2, 0.0),
    'screen_off': ((0.01, 0.012, 0.015, 1), 0.05, 0.0),
    'glass': ((0.8, 0.85, 0.9, 0.15), 0.0, 0.0),
    'carpet_black': ((0.02, 0.02, 0.02, 1), 1.0, 0.0),
    'rubber': ((0.02, 0.02, 0.02, 1), 0.8, 0.0),
    'stitch_grey': ((0.5, 0.5, 0.5, 1), 0.7, 0.0),
    'emblem': ((0.8, 0.1, 0.1, 1), 0.3, 0.3),
    'emissive_white': ((1, 1, 1, 1), 0.2, 0.0),
    'headliner_suede': ((0.035, 0.035, 0.037, 1), 0.95, 0.0),
    'seatbelt': ((0.02, 0.02, 0.02, 1), 0.8, 0.0),
    'mirror': ((0.95, 0.95, 0.95, 1), 0.0, 1.0),
}


def get_material(name):
    if name in MATERIALS:
        return MATERIALS[name]
    base, rough, metal = MATERIAL_DEFS.get(name, ((0.5, 0.5, 0.5, 1), 0.5, 0.0))
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = base
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    if name == 'glass':
        bsdf.inputs['Alpha'].default_value = 0.15
        mat.blend_method = 'BLEND'
    if name == 'emissive_white':
        bsdf.inputs['Emission Color'].default_value = (1, 1, 1, 1)
        bsdf.inputs['Emission Strength'].default_value = 3.0
    MATERIALS[name] = mat
    return mat


def set_material(obj, name):
    mat = get_material(name)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return mat


def tag(obj, component_id, category=None, selectable=True):
    """Store the component id used by the runtime registry."""
    obj.name = component_id
    obj['ct_component'] = component_id
    if category:
        obj['ct_category'] = category
    obj['ct_selectable'] = selectable
    return obj


# ---------------------------------------------------------------------------
# text (emblem placeholders / labels)
# ---------------------------------------------------------------------------

def text_object(name, text, size, origin, u_axis, v_axis, extrude=0.0005, material='emblem', collection='Cockpit', align='CENTER'):
    cu = bpy.data.curves.new(name, type='FONT')
    cu.body = text
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align
    cu.align_y = 'CENTER'
    obj = bpy.data.objects.new(name, cu)
    ensure_collection(collection).objects.link(obj)
    u = Vector(u_axis).normalized(); v = Vector(v_axis).normalized(); n = u.cross(v).normalized()
    m = Matrix((
        (u.x, v.x, n.x, origin[0]),
        (u.y, v.y, n.y, origin[1]),
        (u.z, v.z, n.z, origin[2]),
        (0, 0, 0, 1)))
    obj.matrix_world = m
    obj.data.materials.append(get_material(material))
    return obj
