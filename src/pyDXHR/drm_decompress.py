#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Decompress extracted DRM
"""

from pathlib import Path
import argparse
from pyDXHR.cdcEngine.DRM.CompressedDRM import decompress

parser = argparse.ArgumentParser(description='pyDXHR: Decompress CDRM')
parser.add_argument('-i', '--input', dest='path', help='Input file')

args = parser.parse_args()

with open(args.path, 'rb') as f:
    data = f.read()

decompressed = decompress(data,return_as_bytes=True)
with open(Path(args.path).parent / f"{Path(args.path).stem}_decompressed.drm", 'wb') as f:
    f.write(decompressed)
