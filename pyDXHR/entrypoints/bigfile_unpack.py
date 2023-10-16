#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unpack DXHR Bigfile
Status: Done, tested on PC and console versions
Drag-and-drop works
"""

from pyDXHR.Bigfile.unpack import unpack_to_location
import argparse
import sys

parser = argparse.ArgumentParser(
    prog="pyDXHR Bigfile Unpacker", description="Unpack bigfiles from DXHR"
)

parser.add_argument(
    "source",
    metavar="source",
    type=str,
)

parser.add_argument("-o", "--out", help="output directory", type=str, default=None)

parser.add_argument("-u", "--unknown", action="store_true", help="Get unknown files")

parser.add_argument("-k", "--known", action="store_true", help="Get known files")

args = parser.parse_args()

unpack_to_location(args.source, args.out, args.unknown, args.known)
sys.exit(0)
