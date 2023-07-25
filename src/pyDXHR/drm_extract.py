#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Extract a specific DRM from a Bigfile
"""
import sys

from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.Export.filelist_mock import populate_filelist_directory
from pathlib import Path
import tempfile
from tkinter import filedialog as fd
from tkinter.messagebox import askyesno

file_list = fd.askopenfilename(
    title="Specify path to generic filelist",
    filetypes=(("txt", '*.txt'), ("All files", "*.*")),
)

bigfile = fd.askopenfilename(
    title="Specify path to DXHR BIGFILE.000",
    filetypes=(("BIFGILE", '*.000'), ("All files", "*.*")),
)

try:
    arc = Archive()
    arc.deserialize_from_file(bigfile)
except:
    print("Invalid bigfile")
    sys.exit(-1)

out = True
with tempfile.TemporaryDirectory() as tf:
    try:
        populate_filelist_directory(arc, file_list, tf)
    except:
        print("Invalid filelist")
        sys.exit(-1)

    print("Defaulting to spec 0xFFFFFFFF")
    while out:
        filetypes = (
            ('cdcEngine DRM files', '*.drm'),
            ('All files', '*.*')
        )

        filename = fd.askopenfilename(
            filetypes=filetypes,
            initialdir=tf,
        )

        selected = str(Path(filename).relative_to(tf))

        data = arc.get_from_filename(selected, as_bytes=True, as_raw=True)

        with open(Path(selected).name, "wb") as ff:
            ff.write(data)

        out = askyesno("DRM Extractor", "Extract another DRM?")

    print("Cleaning up...")
