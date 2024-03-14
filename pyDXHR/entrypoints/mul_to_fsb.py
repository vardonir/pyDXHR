#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Convert MUL to FSB
Status: WIP
"""

from pyDXHR.MUL.convert import convert_to_fsb
import argparse
import sys

parser = argparse.ArgumentParser(
    prog="pyDXHR MUL to FSB", description="Convert MUL files to FSB"
)

parser.add_argument(
    "source",
    metavar="source",
    type=str,
)

parser.add_argument("-o", "--out", help="output directory", type=str, default=None)

args = parser.parse_args()

convert_to_fsb(args.source, args.out)
sys.exit(0)
