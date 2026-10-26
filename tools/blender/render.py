"""Headless check renders. Usage inside build: render.render_all(out_dir, engine='WORKBENCH'|'CYCLES')."""
import os
import math
import bpy
from mathutils import Vector
import layout as L

VIEWS = {
    # name: (location, look_at, fov_deg)
    'driver_pov': (L.EYE, (-0.30, 1.4, 0.70), 80),
    'driver_pov_down': (L.EYE, (-0.20, 0.5, 0.45), 80),
    'passenger_pov': (L.PASSENGER_EYE, (0.10, 1.4, 0.70), 80),
    'dash_front': ((0.0, -0.45, 0.95), (0.0, 0.9, 0.70), 75),
    'wheel_closeup': ((-0.37, -0.05, 0.78), (-0.37, 0.46, 0.66), 50),
    'console_top': ((0.0, -0.35, 1.0), (0.0, 0.25, 0.55), 65),
    'driver_seat': ((0.55, 0.05, 0.95), (-0.37, -0.10, 0.55), 62),
    'driver_seat_front': ((-0.30, 0.42, 0.85), (-0.37, -0.15, 0.55), 70),
    'seat_iso': ((-1.4, -0.9, 1.45), (-0.37, -0.05, 0.55), 50),
    'seats_rear_iso': ((0.9, -1.6, 1.5), (0.0, -0.05, 0.55), 55),
    'door_panel': ((-0.05, 0.05, 0.75), (-0.70, 0.10, 0.55), 75),
    'headliner': (L.EYE, (-0.30, 0.0, 1.5), 85),
    'rear_view': (L.EYE, (0.0, -1.5, 0.80), 85),
    'overview': ((1.8, -1.8, 1.9), (0.0, 0.2, 0.55), 55),
    'overview_left': ((-1.9, -1.6, 1.7), (-0.2, 0.2, 0.55), 55),
}


def _camera(name, loc, target, fov):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens_unit = 'FOV'
    cam_data.angle = math.radians(fov)
    cam_data.clip_start = 0.02
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = Vector(loc)
    direction = Vector(target) - Vector(loc)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return cam


def setup_lighting():
    sun = bpy.data.lights.new('Sun', 'SUN')
    sun.energy = 3.0
    so = bpy.data.objects.new('Sun', sun)
    bpy.context.scene.collection.objects.link(so)
    so.rotation_euler = (math.radians(50), math.radians(10), math.radians(-30))
    for i, pos in enumerate([(-0.3, 0.2, 1.0), (0.3, 0.2, 1.0), (0.0, -0.4, 1.0)]):
        pl = bpy.data.lights.new(f'Fill{i}', 'POINT')
        pl.energy = 25
        pl.shadow_soft_size = 0.3
        po = bpy.data.objects.new(f'Fill{i}', pl)
        bpy.context.scene.collection.objects.link(po)
        po.location = pos
    world = bpy.data.worlds.new('World')
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (0.6, 0.7, 0.85, 1)
    bg.inputs[1].default_value = 1.0


HIDE = {
    'driver_seat': ['roof.', 'pillar.', 'glass.', 'doors.passenger', 'mirror.'],
    'driver_seat_front': ['roof.', 'pillar.', 'glass.', 'mirror.'],
    'seat_iso': ['roof.', 'pillar.', 'glass.', 'doors.driver', 'mirror.', 'rear.', 'sill.driver'],
    'seats_rear_iso': ['roof.', 'pillar.', 'glass.', 'mirror.', 'rear.', 'doors.passenger', 'sill.passenger'],
    'overview': ['roof.', 'glass.', 'mirror.'],
}


def render_all(out_dir, views=None, engine='WORKBENCH', size=(1280, 720), samples=32, color='MATERIAL'):
    os.makedirs(out_dir, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH' if engine == 'WORKBENCH' else 'CYCLES'
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    if engine == 'WORKBENCH':
        sh = scene.display.shading
        sh.light = 'STUDIO'
        sh.color_type = color
        sh.show_cavity = True
        sh.cavity_type = 'BOTH'
        sh.show_shadows = True
        sh.show_specular_highlight = True
        scene.display.render_aa = 'FXAA'
    else:
        scene.cycles.samples = samples
        scene.cycles.device = 'CPU'
        scene.cycles.use_denoising = True
        scene.cycles.use_adaptive_sampling = True
        scene.view_settings.view_transform = 'AgX'
        scene.view_settings.look = 'AgX - Medium High Contrast'
    setup_lighting()
    names = views or list(VIEWS.keys())
    for name in names:
        loc, target, fov = VIEWS[name]
        cam = _camera('cam_' + name, loc, target, fov)
        scene.camera = cam
        scene.render.filepath = os.path.join(out_dir, f'{name}.png')
        hidden = []
        for o in bpy.data.objects:
            if o.type in ('MESH', 'FONT') and any(o.name.startswith(pfx) for pfx in HIDE.get(name, [])):
                if not o.hide_render:
                    o.hide_render = True
                    hidden.append(o)
        bpy.ops.render.render(write_still=True)
        for o in hidden:
            o.hide_render = False
        print('RENDERED', scene.render.filepath)
