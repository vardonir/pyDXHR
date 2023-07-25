#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unpacker for Bigfiles
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

# if len(sys.argv) < 2:
#     print("Usage: bigfile_unpack.exe")
#     sys.exit(1)
# else:
file_list = os.getenv("PYDXHR_FILELIST")
if file_list is None:
    print("Error: PYDXHR_FILELIST not set")
    sys.exit(1)
else:
    print("Using filelist: " + file_list)

