#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Extract and convert RenderMesh data to GLTF files
"""

from pathlib import Path
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM
from pyDXHR.cdcEngine.Archive import Archive
import sys
from tkinter import filedialog as fd
from tkinter.messagebox import askyesno, showinfo
from pyDXHR.Export.filelist_mock import populate_unit_selection_list
import tempfile

showinfo(
    title="pyDXHR Unit GLTF converter by vardonir",
    message="This tool will extract and convert DXHR map data to GLTF files.\n"
            "You will need to specify a path to a generic filelist and a path to BIGFILE.000.\n"
            "The tool will then ask you to select a DRM file to convert and a destination for the files.\n"
            "Several empty files in your temp directory will be created for convenience. The output has been "
            "tested on Blender 3.0 and UE5.2."
)

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

with tempfile.TemporaryDirectory() as tf:
    try:
        populate_unit_selection_list(arc, file_list, tf)
    except:
        print("Invalid filelist")
        sys.exit(-1)
    else:
        filetypes = (
            ('cdcEngine DRM files', '*.drm'),
        )

        drm_filename = fd.askopenfilename(
            title="Specify DRM file to convert",
            filetypes=filetypes,
            initialdir=tf,
        )

        showinfo(
            title="pyDXHR Unit GLTF converter",
            message="A directory will be created - the main GLTF "
                    "file will have the same name as the directory."
        )

        dest_path = fd.asksaveasfilename(
            title="Specify destination path",
            filetypes=[("GLTF model", "*.gltf")],
        )

        selected = str(Path(drm_filename).relative_to(tf))

        data = arc.get_from_filename(selected)

        print(f"Loading {selected}")

        # read as unit
        drm = UnitDRM(
            uniform_scale=0.002,
            z_up=True,
        )
        drm.deserialize(
            data,
            archive=arc,
            # split_by_occlusion=True,
        )

        drm.to_gltf(
            save_to=dest_path,
            skip_materials=True
        )

    print("Cleaning up...")
