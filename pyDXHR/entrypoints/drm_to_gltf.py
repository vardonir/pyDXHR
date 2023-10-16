#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Convert a DRM to GLTF
Status: Needs testing
"""


def create_gltf(drm_byte_data, dest_path=None, scale=1.0, z_up=False):
    from pyDXHR.DRM import DRM

    # from pyDXHR.DRM.Section import RenderMesh, Material, RenderResource
    from pyDXHR.export import gltf

    drm = DRM.from_bytes(drm_byte_data)
    drm.open()

    gltf.from_drm(drm, save_to=dest_path, scale=scale, z_up=z_up)

    # mtl = [mat.read() for mat in Material.from_drm(drm)]
    # texs = [tex.read() for tex in RenderResource.from_drm(drm)]


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog="pyDXHR DRM to GLTF", description="Convert DRM models to GLTF"
    )

    parser.add_argument(
        "source",
        metavar="source",
        type=str,
    )

    parser.add_argument("-o", "--out", help="output directory", type=str, default=None)

    parser.add_argument("-s", "--scale", help="scale factor", type=float, default=1.0)

    parser.add_argument(
        "-z", "--z-up", action="store_true", help="Use z-axis as up", default=False
    )

    args = parser.parse_args()

    if args.out is None:
        dest = args.source + ".gltf"
    else:
        dest = args.out

    with open(args.source, "rb") as f:
        data = f.read()
        create_gltf(data, dest_path=dest, scale=args.scale, z_up=args.z_up)

    sys.exit(0)
