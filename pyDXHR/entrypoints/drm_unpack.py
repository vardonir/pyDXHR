#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unpack DRM sections to a directory
Status: TODO
"""


import sys

if len(sys.argv) < 2:
    print("Usage: drm_unpack.exe <input_file>")
    sys.exit(1)
else:
    with open(sys.argv[1], "rb") as f:
        data = f.read()
