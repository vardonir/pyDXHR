#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspect sections in DRM and extract the data
"""
from pathlib import Path
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
import sys


if len(sys.argv) < 2:
    print("Usage: drm_decompress.exe <input_file>")
    sys.exit(1)
else:
    with open(sys.argv[1], 'rb') as f:
        data = f.read()

    drm = DRM()
    drm.deserialize(data)


    # with open(Path(sys.argv[1]).parent / f"{Path(sys.argv[1]).stem}_decompressed.drm", 'wb') as f:
    #     f.write(decompressed)
