#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bigfile repacker
args: path to pc-w
"""

import sys
from pathlib import Path
from tkinter import filedialog as fd
from pyDXHR.utils import crc32bzip2
from tkinter.messagebox import askyesno

file_list = fd.askopenfilename(
    title="Specify path to generic filelist",
    filetypes=(("txt", '*.txt'), ("All files", "*.*")),
)

pcw_dir = fd.askdirectory(
    title="Specify path to pc-w",
    mustexist=True
)

bigfile = fd.askopenfilename(
    title="Specify path to DXHR BIGFILE.000",
    filetypes=(("BIFGILE", '*.000'), ("All files", "*.*")),
)

from pyDXHR.cdcEngine.Archive import Archive

# load the data
arc = Archive()
arc.deserialize_from_file(bigfile)

# for all the files in pcw_dir, get the entry data and keep it in a list
# then read the data from those files, replace the uncompressed size value
# and the entry data

arc.Entries = []

# append the new entries here

new_bigfile = arc.serialize()

# look for the mods folder
# if it doesn't exist, create it
if not (Path(bigfile).parent / "mods").is_dir():
    mods_folder_yesno = askyesno("DXHR Bigfile Repack", "mods folder not found. Create?")
    if mods_folder_yesno:
        (Path(bigfile).parent / "mods").mkdir()
mods_folder = Path(bigfile).parent / "mods"

# ask for the filename of the mod
mod_filename = fd.asksaveasfilename(
    initialdir=mods_folder,
    defaultextension=".000",
)

for idx, byte_data in enumerate(new_bigfile):
    output_file = Path(mod_filename).parent / f"{Path(mod_filename).stem}.00{idx}"

    print(f"Writing to {Path(output_file).name}")
    with open(output_file, "wb") as f:
        f.write(byte_data)

print("Final checks")
new_arc = Archive()
new_arc.deserialize_from_file(fr"{mod_filename}.000")
