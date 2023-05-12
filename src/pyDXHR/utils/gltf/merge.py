import pygltflib as gl
from pathlib import Path
import json
from tqdm import tqdm
from copy import copy
import numpy as np
from typing import *


def apply_node_transformations(node: gl.Node, **kwargs):
    trs_mat = kwargs.get("trs_matrix")
    if trs_mat is not None:
        if isinstance(trs_mat, np.ndarray):
            node.matrix = trs_mat.flatten().tolist()
            return node
        else:
            raise Exception

    node.scale = kwargs.get("scale")
    node.rotation = kwargs.get("rotation")
    node.translation = kwargs.get("translation")
    return node


def merge_single_node_gltf(
        output_path: str | Path,
        location_table: dict,
        split_objects_to_separate_node: bool = False,
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
    top_node = apply_node_transformations(top_node, **kwargs)

    # if trs_matrix is not None:
    #     top_node.matrix = trs_matrix.flatten().tolist()
    # top_node.scale = kwargs.get("scale")
    # top_node.rotation = kwargs.get("rotation")
    # top_node.translation = kwargs.get("translation")

    # materials and images
    compiled_materials = {
        m.name: copy(m)
        for _, f in gltf_files
        for m in f.materials
    }

    # the materials are just copied in bulk to the GLTF file
    merged_file.materials = list(compiled_materials.values())
    mat_id_list = list(compiled_materials.keys())
    # to get the mat index given a cdcMatID: mat_id_list.index(cdcMatID)

    compiled_images = {
        i.name: copy(i)
        for _, f in gltf_files
        for i in f.images
    }

    # the URI attached to the image needs to be updated before it gets attached
    for im in compiled_images.values():
        im.uri = str(Path(*Path(im.uri).parts[1:]))
        merged_file.images.append(im)

    im_id_list = list(compiled_images.keys())

    # then the textures need to be copied
    if len([t for _, f in gltf_files for t in f.textures]) != 0:
        compiled_textures = {
            t.name: copy(t)
            for _, f in gltf_files
            for t in f.textures
        }

        merged_file.textures = list(compiled_textures.values())
        tex_id_list = list(compiled_textures.keys())
        assert len(im_id_list) == len(tex_id_list)

        for tex_name, gltf_tex in compiled_textures.items():
            gltf_tex.source = im_id_list.index(tex_name)
    else:
        tex_id_list = None

    indices: Dict[str, Set[int]] = {
        "ALL": set(),

        "stream": set(),
        "imf_ext": set(),
        "obj": set(),
        "imf_int": set(),
        "cell": set(),
        "occlusion": set(),
    }

    # transfer accessors / buffers / meshes
    pbar = tqdm(gltf_files) if kwargs.get("verbose", True) else gltf_files
    for path, f in pbar:
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
                indices[path.parent.stem].add(current_node_index)

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

            cdc_mat_id = prim.extras["cdcMatID"]
            prim.material = mat_id_list.index(cdc_mat_id)

    # transfer materials / textures
    if tex_id_list is not None:
        pbar = tqdm(merged_file.materials) if kwargs.get("verbose", True) else merged_file.materials
        for mat in pbar:
            if mat.pbrMetallicRoughness:
                mat.pbrMetallicRoughness.baseColorTexture.index = tex_id_list.index(mat.extras["diffuse"])
            if mat.normalTexture:
                mat.normalTexture.index = tex_id_list.index(mat.extras["normal"])

    # finalize node tree
    merged_file.scene = 0
    scene.nodes = [len(merged_file.nodes)]  # scene node is top node only
    merged_file.nodes.append(top_node)

    if split_objects_to_separate_node:
        for name, idx in indices.items():
            if name == "ALL":
                pass
            else:
                if len(list(indices[name])):
                    node = gl.Node(
                        name=name,
                        children=list(indices[name])
                    )

                    node_index = len(merged_file.nodes)
                    merged_file.nodes.append(node)
                    top_node.children.append(node_index)
    else:
        top_node.children = list(indices['ALL'])

    merged_file.save(outfile)

    # TODO: uncomment this when materials are fixed
    if kwargs.get("test_generate_material", True):
        for_checking = set()
        pbar = tqdm(merged_file.materials) if kwargs.get("verbose", True) else merged_file.materials
        for mat in pbar:
            for k, v in mat.extras.items():
                if len(v.split(",")) > 1:
                    for_checking.add(mat.name)
                    break
            if len(set(mat.extras.keys()).difference({"diffuse", "normal", "colors"})):
                for_checking.add(mat.name)
                continue

            if "colors" in mat.extras:
                if len([c for c in mat.extras['colors'].split(",") if "dummy" not in c]):
                    for_checking.add(mat.name)
                    continue

        with open(Path(output_path) / f"materials.csv", "w") as f:
            for i in for_checking:
                f.write(f"{i} \n")


def merge_multinode_gltf(
        output_path: str | Path,
        **kwargs,
):
    pass
    # top_level_gltf_files = [(f, gl.GLTF2().load(f))
    #                         for f in Path(output_path).rglob("*.gltf")
    #                         if len(f.relative_to(output_path).parts) == 2]
    #
    # outfile = Path(output_path) / f"{Path(output_path).stem}.gltf"
    #
    # merged_file = gl.GLTF2()
    # scene = gl.Scene(
    #     name=Path(output_path).stem
    # )
    # merged_file.scenes.append(scene)
    #
    # # the topmost node that will handle scaling for the entire file
    # top_node = gl.Node(
    #     name=Path(output_path).stem,
    # )
    # top_node = apply_node_transformations(top_node, **kwargs)
    #
    # breakpoint()
