from typing import List

import pygltflib as gl
from pathlib import Path

from Bigfile import Bigfile
from pyDXHR.DRM import DRM
from pyDXHR.DRM.unit import UnitDRM
from pyDXHR.export import gltf
import tempfile


def from_drm(drm: UnitDRM, bigfile: Bigfile,
             save_to: Path | str,
             scale: float = 1.0, z_up: bool = False, lumen: bool = False) -> None:
    temp_dir = Path(tempfile.gettempdir()) / "pyDXHR"
    temp_dir.mkdir(parents=True, exist_ok=True)

    node_list: List[gl.Node] = []

    if not len(drm.obj_map):
        drm.read_objects()

    object_list = [line.split(",") for line in bigfile.read("objectlist.txt").decode("utf-8").split("\r\n")]
    object_list = {int(line[0]): line[1] for line in object_list if len(line) == 2}
    parsed_object_map = {object_list[obj_id]: trs_list for obj_id, trs_list in drm.obj_map.items()}

    objs_node = gl.Node(
        name="objects",
    )
    objs_node.extras |= {
        "node_type": "category"
    }
    node_list.append(objs_node)

    for obj_name, trs_list in parsed_object_map.items():

        obj_node = gl.Node(
            name=obj_name,
        )
        obj_node.extras |= {
            "node_type": "object"
        }
        node_list.append(obj_node)

        drm = DRM.from_bigfile(obj_name, bigfile)
        gltf.from_drm(drm=drm, save_to=temp_dir / (obj_name + ".gltf"), scale=scale, z_up=z_up, lumen=lumen)
        obj_gltf = gl.GLTF2().load(temp_dir / (obj_name + ".gltf"))


        print(trs_list)

    breakpoint()

    if not len(drm.int_imf_map) or not len(drm.ext_imf_map):
        drm.read_imfs()

    int_imf_node = gl.Node(
        name="int_imf",
    )

    ext_imf_node = gl.Node(
        name="ext_imf",
    )