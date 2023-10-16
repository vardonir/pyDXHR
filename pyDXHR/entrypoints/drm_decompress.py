#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Decompress extracted DRM
Status: Done
"""

import sys
from pathlib import Path

from pyDXHR.DRM import decompress

if len(sys.argv) < 2:
    print("Usage: drm_decompress.exe <input_file>")
    sys.exit(1)
else:
    with open(sys.argv[1], "rb") as f:
        data = f.read()

    decompressed = decompress(data)
    with open(
        Path(sys.argv[1]).parent / f"{Path(sys.argv[1]).stem}_decompressed.drm", "wb"
    ) as f:
        f.write(decompressed)

    sys.exit(0)
