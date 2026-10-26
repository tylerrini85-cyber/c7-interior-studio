"""Build the C7 cockpit. Run: blender -b --python tools/blender/build.py -- [--render] [--parts cabin,dash,...] [--engine WORKBENCH|CYCLES]"""
import os
import sys
import argparse
import importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))

import bpy  # noqa: E402
import lib  # noqa: E402

ALL_PARTS = ['cabin', 'dashboard', 'steering', 'console', 'seats', 'doors']


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--parts', default=','.join(ALL_PARTS))
    ap.add_argument('--render', action='store_true')
    ap.add_argument('--views', default='')
    ap.add_argument('--engine', default='WORKBENCH')
    ap.add_argument('--out', default=os.path.join(ROOT, 'public', 'models', 'c7-cockpit.glb'))
    ap.add_argument('--renders', default=os.path.join(ROOT, 'docs', 'renders'))
    ap.add_argument('--no-export', action='store_true')
    ap.add_argument('--skip-variants', action='store_true')
    ap.add_argument('--size', default='1280x720')
    ap.add_argument('--color', default='MATERIAL')
    args = ap.parse_args(argv)

    lib.reset_scene()
    lib.ensure_collection('Cockpit')
    for name in [p for p in args.parts.split(',') if p]:
        mod = importlib.import_module(f'parts.{name}')
        print(f'--- building {name}')
        mod.build()

    # remove boolean cutters from export
    for o in list(bpy.data.objects):
        if o.get('ct_cutter'):
            o.hide_render = True

    if not args.no_export:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        bpy.ops.export_scene.gltf(filepath=args.out, export_format='GLB', export_apply=True, export_yup=True,
                                  export_extras=True, export_cameras=False, export_lights=False,
                                  export_texcoords=True, export_normals=True, export_materials='EXPORT',
                                  use_visible=True)
        print('EXPORTED', args.out, os.path.getsize(args.out), 'bytes')
    if args.render:
        import render
        w, h = [int(v) for v in args.size.split('x')]
        views = [v for v in args.views.split(',') if v] or None
        render.render_all(args.renders, views=views, engine=args.engine, size=(w, h), color=args.color)

    if not args.no_export and not args.skip_variants:
        import parts.steering as steering
        vdir = os.path.join(os.path.dirname(args.out), 'variants')
        os.makedirs(vdir, exist_ok=True)
        for variant in steering.VARIANTS[1:]:
            lib.reset_scene(); lib.MATERIALS.clear(); lib.ensure_collection('Cockpit')
            steering.build(variant)
            path = os.path.join(vdir, f'steering_{variant}.glb')
            bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_apply=True, export_yup=True, export_extras=True, export_cameras=False, export_lights=False, use_visible=True)
            print('EXPORTED', path, os.path.getsize(path), 'bytes')
        import parts.console as console
        for variant in console.SHIFTER_VARIANTS[1:]:
            lib.reset_scene(); lib.MATERIALS.clear(); lib.ensure_collection('Cockpit')
            console.build_shifter(variant)
            path = os.path.join(vdir, f'shifter_{variant}.glb')
            bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_apply=True, export_yup=True, export_extras=True, export_cameras=False, export_lights=False, use_visible=True)
            print('EXPORTED', path, os.path.getsize(path), 'bytes')
        if hasattr(importlib.import_module('parts.seats'), 'VARIANTS') if os.path.exists(os.path.join(HERE, 'parts', 'seats.py')) else False:
            seats = importlib.import_module('parts.seats')
            for variant in seats.VARIANTS[1:]:
                lib.reset_scene(); lib.MATERIALS.clear(); lib.ensure_collection('Cockpit')
                seats.build(variant)
                path = os.path.join(vdir, f'seats_{variant}.glb')
                bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_apply=True, export_yup=True, export_extras=True, export_cameras=False, export_lights=False, use_visible=True)
                print('EXPORTED', path, os.path.getsize(path), 'bytes')


main()
