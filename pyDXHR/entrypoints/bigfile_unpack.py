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

parser.add_argument(
    "-o",
    "--out",
    help="output directory",
    type=str,
    default=None
)

parser.add_argument(
    "-u",
    "--skip-unknown",
    action="store_true",
    help="Skip unknown files"
)

parser.add_argument(
    "-k",
    "--skip-known",
    action="store_true",
    help="Skip known files"
)

args = parser.parse_args()

if args.skip_unknown and args.skip_known:
    # what are you doing lol
    print("???")
    sys.exit(1)
else:
    unpack_to_location(args.source, args.out, args.skip_unknown, args.skip_known)
    sys.exit(0)
