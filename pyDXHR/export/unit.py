"""


"""

import shutil
import json
from typing import List, Dict, Optional
from copy import copy

import kaitaistruct
import numpy as np
import pygltflib as gl
from pathlib import Path

from Bigfile import Bigfile
from pyDXHR.DRM import DRM
from pyDXHR.DRM.Section import RenderMesh, Material
from pyDXHR.DRM.unit import UnitDRM
from pyDXHR.export import gltf
import tempfile
from scipy.spatial.transform import Rotation


def from_drm(drm: UnitDRM,
             bigfile: Bigfile,
             save_to: Path | str,
             scale: float = 1.0,
             z_up: bool = False,
             **kwargs
             ) -> None:
    if len(Path(save_to).suffix) != 0:
        save_to = Path(save_to).parent
        save_to.mkdir(parents=True, exist_ok=True)

    # stream data
    if kwargs.get("stream", True):
        stream_gltf_list = []
        stream_mat_list = []
        if len(drm.streamgroup_map):
            for (streamgroup_path, streamgroup_name), trs in drm.streamgroup_map.items():
                stream_drm = DRM.from_bigfile(rf"streamgroups\{streamgroup_name}.drm", bigfile)
                stream_drm.open()

                mat_list = Material.from_drm(stream_drm)
                for mat in mat_list:
                    mat.read()
                stream_mat_list.extend(mat_list)

                for sec in stream_drm.sections:
                    stream_gltf = gltf.to_temp(sec)
                    if stream_gltf is not None:
                        stream_gltf_list.append(stream_gltf)

                gltf.merge(
                    gltf_list=stream_gltf_list,
                    save_to=Path(save_to) / (streamgroup_name + '.gltf'),
                    scale=scale,
                    z_up=z_up,
                    mat_list=stream_mat_list,
                    drm_name=stream_drm.name.replace('.drm', ''),
                )

    # internal data
    mat_list = Material.from_drm(drm)
    for mat in mat_list:
        mat.read()

    if kwargs.get("cell", True):
        cell_gltf_list = []
        if len(drm.cell_map):

            for (cell_name, cell_sec_id), sec in drm.cell_section_data.items():
                cell_gltf = gltf.to_temp(sec)
                cell_gltf_list.append(cell_gltf)

            gltf.merge(
                gltf_list=cell_gltf_list,
                save_to=Path(save_to) / (drm.name.replace('.drm', '') + "_cells.gltf"),
                scale=scale,
                z_up=z_up,
                mat_list=mat_list,
                drm_name=f"{drm.name.replace('.drm', '')}_cell",
            )

    if kwargs.get("int_imf", True) or kwargs.get("ext_imf", True):
        if not len(drm.int_imf_map) or not len(drm.ext_imf_map):
            drm.read_imfs()

        if kwargs.get("int_imf", True):
            int_imf_gltf_dict: Dict[int, gl.GLTF2] = {}
            for sec_id, trs_list in drm.int_imf_map.items():
                imf_gltf = gltf.to_temp(drm.get_section_from_id(sec_id))
                int_imf_gltf_dict[sec_id] = imf_gltf

            gltf.merge_with_table(
                gltf_dict=int_imf_gltf_dict,
                loc_table=drm.int_imf_map,
                save_to=Path(save_to) / (drm.name.replace('.drm', '') + "_int_imf.gltf"),
                scale=scale,
                z_up=z_up,
                mat_list=mat_list,
                drm_name=f"{drm.name.replace('.drm', '')}_int_imf",
            )

            breakpoint()

        if kwargs.get("ext_imf", True):
            ext_imf_gltf_dict: Dict[str, gl.GLTF2] = {}
            for imf_name, trs_list in drm.ext_imf_map.items():
                data = bigfile.read(imf_name)
                imf = DRM.from_bytes(data)
                imf.open()

                breakpoint()

    if kwargs.get("obj", True):
        if not len(drm.obj_map):
            drm.read_objects()

        object_list = [line.split(",") for line in bigfile.read("objectlist.txt").decode("utf-8").split("\r\n")]
        object_list = {int(line[0]): line[1] for line in object_list if len(line) == 2}
        parsed_object_map = {object_list[obj_id]: trs_list for obj_id, trs_list in drm.obj_map.items()}

        breakpoint()
