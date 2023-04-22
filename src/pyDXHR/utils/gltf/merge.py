import pygltflib as gl
from pathlib import Path
import json
from tqdm import tqdm
from copy import copy
import numpy as np
from typing import *


def merge_single_node_gltf(
        output_path: str | Path,
        location_table: dict,
        split_objects_to_separate_node: bool = False,
        trs_matrix: Optional[np.ndarray] = None,
        **kwargs,
):

    gltf_files = [(f, gl.GLTF2().load(f)) for f in Path(output_path).rglob("*.gltf")]

    outfile = Path(output_path) / f"{Path(output_path).stem}.gltf"

    # initialize the destination
    merged_file = gl.GLTF2()
    scene = gl.Scene(
        name=Path(output_path).stem
    )
    merged_file.scenes.append(scene)

    # the topmost node that will handle scaling for the entire file
    top_node = gl.Node(
        name=Path(output_path).stem,
    )
    if trs_matrix is not None:
        top_node.matrix = trs_matrix.flatten().tolist()
    top_node.scale = kwargs.get("scale")
    top_node.rotation = kwargs.get("rotation")
    top_node.translation = kwargs.get("translation")

    # materials and images
    compiled_materials = {
        m.name: copy(m)
        for _, f in gltf_files
        for m in f.materials
    }

    merged_file.materials = list(compiled_materials.values())
    mat_id_list = list(compiled_materials.keys())
    # to get the index given a cdcMatID: mat_id_list.index(cdcMatID)

    compiled_images = {
        i.name: copy(i)
        for _, f in gltf_files
        for i in f.images
    }

    for im in compiled_images.values():
        im.uri = str(Path(*Path(im.uri).parts[1:]))
        merged_file.images.append(im)

    indices: Dict[str, Set[int]] = {
        "OBJ": set(),
        "NON_OBJ": set(),
        "ALL": set(),
    }
    count = 0
    for path, f in tqdm(gltf_files):
        # if count == 2: break
        # count += 1

        assert len(f.accessors) == len(f.bufferViews)
        assert len(f.buffers) == 1
        assert len(f.nodes) == 1
        assert len(f.meshes) == 1

        if f.buffers[0].byteLength == 0:
            continue

        mesh = copy(f.meshes[0])

        # create new nodes for the transformations
        locs = location_table[path.stem]
        for idx_loc, loc in enumerate(locs):
            node = copy(f.nodes[0])
            node.matrix = loc
            node.mesh = len(merged_file.meshes)
            node.name = f"{node.name} | {idx_loc + 1}"

            current_node_index: int = len(merged_file.nodes)
            indices["ALL"].add(current_node_index)

            if split_objects_to_separate_node:
                if path.parent.stem == "obj":
                    indices["OBJ"].add(current_node_index)
                else:
                    indices["NON_OBJ"].add(current_node_index)

            merged_file.nodes.append(node)

        merged_file.meshes.append(mesh)
        buffer: gl.Buffer = copy(f.buffers[0])
        buffer.uri = str(path.relative_to(output_path).parent / f"{path.relative_to(output_path).stem}.bin")

        acc_cursor = len(merged_file.accessors)
        for o_acc, o_bv in zip(f.accessors, f.bufferViews):
            acc = copy(o_acc)
            bv = copy(o_bv)

            bv.buffer = len(merged_file.buffers)
            bv.name = None
            acc.name = None
            acc.bufferView += acc_cursor

            merged_file.accessors.append(acc)
            merged_file.bufferViews.append(bv)

        merged_file.buffers.append(buffer)

        prim: gl.Primitive
        for prim in mesh.primitives:
            attribute_dict = json.loads(prim.attributes.to_json())
            revised_attrs = {
                attr: attr_idx + acc_cursor
                for attr, attr_idx in attribute_dict.items()
                if attr_idx is not None
            }

            prim.attributes = gl.Attributes(**revised_attrs)
            prim.indices += acc_cursor

            cdcMatID = prim.extras["cdcMatID"]
            prim.material = mat_id_list.index(cdcMatID)

    merged_file.scene = 0
    scene.nodes = [len(merged_file.nodes)]  # scene node is top node only
    merged_file.nodes.append(top_node)

    if len(indices['OBJ']):
        obj_node = gl.Node(
            name="OBJ",
            children=list(indices['OBJ'])
        )
        imf_stream_node = gl.Node(
            name="NON_OBJ",
            children=list(indices['NON_OBJ'])
        )

        obj_node_index = len(merged_file.nodes)
        merged_file.nodes.append(obj_node)

        imf_stream_node_index = len(merged_file.nodes)
        merged_file.nodes.append(imf_stream_node)

        top_node.children = [obj_node_index, imf_stream_node_index]
    else:
        top_node.children = list(indices['ALL'])

    merged_file.save(outfile)


def merge_multinode_gltf(
        output_path: str | Path,
        trs_matrix: Optional[np.ndarray] = None,
        **kwargs,
):
    pass
