#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unpack DRM sections to a directory
Status: Needs testing
"""


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from pyDXHR.DRM import drm_unpack_from_bytes

    if len(sys.argv) < 2:
        print("Usage: drm_unpack.exe <input_file>.drm")
        sys.exit(1)
    else:
        with open(sys.argv[1], "rb") as f:
            data = f.read()

        out = Path(sys.argv[1]).parent

    drm_unpack_from_bytes(
        drm_byte_data=data, drm_name=Path(sys.argv[1]).stem, unpack_destination=out
    )

    sys.exit(0)
