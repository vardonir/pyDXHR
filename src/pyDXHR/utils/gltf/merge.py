import pygltflib as gl
from pathlib import Path
import json
from tqdm import tqdm
from copy import copy
import numpy as np
from typing import *
from pyDXHR.utils import create_directory, get_file_size


def generate_occlusion_mat():
    return gl.Material(
        name="M_Occlusion",
        pbrMetallicRoughness=gl.PbrMetallicRoughness(
            baseColorFactor=[0, 0, 0, 0],  # RGBA
        ),
        doubleSided=True,
        alphaMode=gl.MASK,
        alphaCutoff=0.0
    )


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
    split_by_occlusion = kwargs.get("split_by_occlusion", False)
    if split_by_occlusion:
        split_objects_to_separate_node = False

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
        if im.uri:
            im.uri = "/".join((Path(*Path(im.uri).parts[1:])).parts)
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

    empty_image_buffer = None
    empty_image_buffer_view = None

    occlusion_mat = []
    # transfer accessors / buffers / meshes
    pbar = tqdm(gltf_files) if kwargs.get("verbose", True) else gltf_files
    for path, f in pbar:

        category_name = path.parent.parts[-1]

        empty_image_buffer_view_list = [(idx, bv) for idx, bv in enumerate(f.bufferViews) if bv.name == "dummyblack"]
        if len(empty_image_buffer_view_list) == 1:
            empty_image_bv_index, empty_image_buffer_view = empty_image_buffer_view_list[0]
            f.bufferViews.pop(empty_image_bv_index)
        else:
            breakpoint()

        if len(f.buffers) == 2:
            empty_image_buffer = copy(f.buffers[1])
            f.buffers.pop(1)

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
            node.extras |= {
                "filename": path.stem,
                "original_name": f.nodes[0].name,
                "category": category_name,
            }
            node.name = f"{node.name} | {idx_loc + 1}"

            current_node_index: int = len(merged_file.nodes)
            indices["ALL"].add(current_node_index)

            if split_objects_to_separate_node:
                indices[path.parent.stem].add(current_node_index)

            merged_file.nodes.append(node)

        merged_file.meshes.append(mesh)
        buffer: gl.Buffer = copy(f.buffers[0])
        buffer.uri = "/".join((path.relative_to(output_path).parent / f"{path.relative_to(output_path).stem}.bin").parts)

        acc_cursor = len(merged_file.accessors)
        for o_acc, o_bv in zip(f.accessors, f.bufferViews):
            acc = copy(o_acc)
            bv = copy(o_bv)

            bv.buffer = len(merged_file.buffers)
            bv.name = path.relative_to(output_path).stem
            acc.name = path.relative_to(output_path).stem
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

            # look for the materials used by meshes that are tagged "occlusion"
            if split_by_occlusion and category_name == "occlusion":
                occlusion_mat.append(mat_id_list.index(cdc_mat_id))

    # transfer materials / textures
    if tex_id_list is not None:
        pbar = tqdm(merged_file.materials) if kwargs.get("verbose", True) else merged_file.materials
        for mat in pbar:
            if mat.extras.get("diffuse"):
                mat.pbrMetallicRoughness.baseColorTexture.index = tex_id_list.index(mat.extras.get("diffuse").split(",")[0])
            if mat.extras.get("normal"):
                mat.normalTexture.index = tex_id_list.index(mat.extras.get("normal").split(",")[0])

    if empty_image_buffer_view is not None and empty_image_buffer is not None:
        dummyblack_tex = [t for t in merged_file.textures if t.name == "dummyblack"][0]
        dummyblack_img_idx, dummyblack_img = [(idx, i) for idx, i in enumerate(merged_file.images) if i.name == "dummyblack"][0]

        empty_image_buffer_view.buffer = len(merged_file.buffers)
        dummyblack_img.bufferView = len(merged_file.bufferViews)

        merged_file.bufferViews.append(empty_image_buffer_view)
        merged_file.buffers.append(empty_image_buffer)
        dummyblack_tex.source = dummyblack_img_idx

    # finalize node tree
    merged_file.scene = 0
    scene.nodes = [len(merged_file.nodes)]  # scene node is top node only
    merged_file.nodes.append(top_node)

    if split_by_occlusion:
        from pyDXHR.Export.ProjectSIX.UnitCategorize import categorize_by_bounds

        categorized_files, boxes = categorize_by_bounds(output_path, location_table)
        indices = {b: set() for b in boxes.keys()}
        indices |= {"OUT": set()}
        for index, n in enumerate(merged_file.nodes):
            if "filename" in n.extras:
                location = categorized_files.get((n.extras["filename"], tuple(n.matrix)), "OUT")
                indices[location].add(index)

        for name, idx in indices.items():
            np_arr_bounds = boxes.get(name, np.zeros((2, 3)))

            node = gl.Node(
                name=f"BoundingBox_{name}",
                children=list(idx),
                extras={
                    "bounds": str(np_arr_bounds.round(2).flatten().tolist()),
                    "parent_unit": Path(output_path).stem
                }
            )

            node_index = len(merged_file.nodes)
            merged_file.nodes.append(node)
            top_node.children.append(node_index)

        for idx in set(occlusion_mat):
            merged_file.materials[idx] = generate_occlusion_mat()

    elif split_objects_to_separate_node:
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
                if isinstance(v, list):
                    break
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
    import shutil
    import ast

    top_level_gltf_files = [f
                            for f in Path(output_path).rglob("*.gltf")
                            if len(f.relative_to(output_path).parts) == 2]

    texture_folders = [f
                       for f in Path(output_path).rglob("*/textures")
                       if f.is_dir()]

    # copy textures from each GLTF folder to top
    merged_texture_dir = create_directory(
        save_to=Path(output_path) / "textures",
        action=kwargs.get("action", "overwrite")
    )
    merged_buffers_dir = create_directory(
        save_to=Path(output_path) / "buffers",
        action=kwargs.get("action", "overwrite")
    )

    outfile = Path(output_path) / f"{Path(output_path).stem}.gltf"

    image_paths = {}
    for f in texture_folders:
        for im in f.glob("*.png"):
            image_paths[im.stem] = im
            shutil.copy(im, merged_texture_dir)

    merged_file = gl.GLTF2()
    scene = gl.Scene(
        name=Path(output_path).stem
    )
    merged_file.scenes.append(scene)

    top_node = gl.Node(
        name=Path(output_path).stem + "__masterunit",
    )
    top_node = apply_node_transformations(top_node, **kwargs)
    top_node_idx = len(merged_file.nodes)

    scene.nodes.append(top_node_idx)
    merged_file.nodes.append(top_node)

    # compile images
    for hexTexId, im_path in image_paths.items():
        im_node = gl.Image(
            name=f"T_{hexTexId}",
            uri=str(Path(*im_path.relative_to(output_path).parts[1:])),
            extras={
                "cdcTextureID": int(hexTexId, 16),
            }
        )
        merged_file.images.append(im_node)

    textures = {}
    materials = {}
    buffers = {}

    mesh_node_table = {}
    occlusion_node_table = {}
    unit_node_table = {}

    mesh_table = {}
    vtx_acc_bv_table = {}
    prim_acc_bv_table = {}

    for f in top_level_gltf_files:
        gltf = gl.GLTF2().load(f)

        for mat in gltf.materials:
            mat_idx = len(merged_file.materials)
            if mat.name not in materials:
                merged_file.materials.append(mat)
                materials[mat.name] = mat_idx

        for tex in gltf.textures:
            tex_idx = len(merged_file.textures)
            if tex.name not in textures:
                merged_file.textures.append(tex)
                textures[tex.name] = tex_idx

        assert len(gltf.meshes) == len(gltf.buffers)
        assert len(gltf.accessors) == len(gltf.bufferViews)

        # transfer nodes
        for node in gltf.nodes:
            node_idx = len(merged_file.nodes)

            if "bounds" in node.extras:
                if node.name in occlusion_node_table and node.name != "BoundingBox_OUT":
                    breakpoint()
                if node.name == "BoundingBox_OUT":
                    occlusion_node_table[f.stem] = node_idx
                else:
                    occlusion_node_table[node.name] = node_idx
            elif not node.children:  # if a node has no children, then it's a node for a mesh
                node_mesh_name = node.extras["original_name"]
                if node_mesh_name not in mesh_node_table:
                    mesh_node_table[node_mesh_name] = []
                mesh_node_table[node_mesh_name].append(node_idx)
            elif node.name == f.stem:
                if node.name in unit_node_table:
                    breakpoint()
                unit_node_table[node.name] = node_idx
            else:
                breakpoint()

            merged_file.nodes.append(node)
            node.children = []

        # transfer buffers
        for buf in gltf.buffers:
            buf_idx = len(merged_file.buffers)
            buffer_file = f.parent / buf.uri
            buffer_filename = Path(buf.uri).stem
            assert buffer_file.is_file()
            assert get_file_size(buffer_file) == buf.byteLength

            key = (buffer_filename, buf.extras["name"])
            if key not in buffers:
                dest = merged_buffers_dir / buf.uri
                dest.parent.mkdir(exist_ok=True)
                shutil.copy(buffer_file, dest)
                merged_file.buffers.append(buf)
                buffers[key] = buf_idx
                buf.uri = "/".join((dest.relative_to(output_path)).parts)
                assert get_file_size(dest) == buf.byteLength
            else:
                existing_buffer = merged_file.buffers[buffers[key]]
                assert buf.byteLength == existing_buffer.byteLength
                if Path(buf.uri).stem != Path(existing_buffer.uri).stem:
                    breakpoint()

        mesh: gl.Mesh
        for mesh in gltf.meshes:
            merged_gltf_mesh_idx = len(merged_file.meshes)
            if mesh.name in mesh_table:
                if mesh.name == "RenderTerrain_00002f1f":
                    breakpoint()

                continue
            merged_file.meshes.append(mesh)
            mesh_table[mesh.name] = merged_gltf_mesh_idx

        for acc, bv in zip(gltf.accessors, gltf.bufferViews):
            acc_bv_idx = len(merged_file.bufferViews)

            mesh_name = bv.extras["MESH_NAME"]
            mesh_idx = bv.extras["MESH_IDX"]

            prim_idx = bv.extras.get("PRIM_IDX")
            vtx_sem_name = bv.extras.get("VTX_SEM")

            bv.buffer = buffers[(bv.name, mesh_name)]
            acc.bufferView = acc_bv_idx

            if prim_idx is not None:
                if mesh_name not in prim_acc_bv_table:
                    prim_acc_bv_table[mesh_name] = {}

                    if (mesh_idx, prim_idx) in prim_acc_bv_table[mesh_name]:
                        continue

                prim_acc_bv_table[mesh_name][(mesh_idx, prim_idx)] = acc_bv_idx

                merged_file.accessors.append(acc)
                merged_file.bufferViews.append(bv)
            elif vtx_sem_name is not None:
                if mesh_name not in vtx_acc_bv_table:
                    vtx_acc_bv_table[mesh_name] = {}

                    if (mesh_idx, vtx_sem_name) in vtx_acc_bv_table[mesh_name]:
                        continue

                vtx_acc_bv_table[mesh_name][(mesh_idx, vtx_sem_name)] = acc_bv_idx

                merged_file.accessors.append(acc)
                merged_file.bufferViews.append(bv)
            else:
                raise Exception

    for m_name, m_idx in mesh_table.items():
        mesh = merged_file.meshes[m_idx]
        assert mesh.name == m_name

        for _, prim in enumerate(mesh.primitives):
            prim_attr = copy(json.loads(prim.attributes.to_json()))
            prim_mesh_idx = prim.extras["MESH_IDX"]
            prim_idx = prim.extras["PRIM_IDX"]

            revised_attrs = {
                vsname: vtx_acc_bv_table[m_name][(prim_mesh_idx, vsname)]
                for vsname, idx
                in prim_attr.items()
                if idx is not None
            }

            if not len([i for i in revised_attrs.values() if i is not None]):
                breakpoint()

            prim.attributes = gl.Attributes(**revised_attrs)
            prim.indices = prim_acc_bv_table[m_name][(prim_mesh_idx, prim_idx)]

            cdc_mat_id = prim.extras["cdcMatID"]
            prim.material = materials.get(cdc_mat_id)

    # finalize nodes

    # check for duplicates in the tables:
    mn_set = set(i for il in mesh_node_table.values() for i in il)
    occn_set = set(i for i in occlusion_node_table.values())
    unitn_set = set(i for i in unit_node_table.values())

    assert len(mn_set) == len([i for il in mesh_node_table.values() for i in il])
    assert len(occn_set) == len([i for i in occlusion_node_table.values()])
    assert len(unitn_set) == len([i for i in unit_node_table.values()])

    assert len(mn_set.intersection(occn_set)) == 0
    assert len(occn_set.intersection(unitn_set)) == 0
    assert len(unitn_set.intersection(mn_set)) == 0

    # check the number of nodes in the tables are as expected
    a = mn_set.union(occn_set).union(unitn_set)
    assert 1 + len(a) == len(merged_file.nodes)
    assert list(range(1, 1+len(a))) == sorted(list(a))

    # unit nodes are children of the top node
    for name, n_idx in unit_node_table.items():
        merged_file.nodes[n_idx].rotation = None
        merged_file.nodes[n_idx].scale = None
        merged_file.nodes[top_node_idx].children.append(n_idx)

    occlusion_bounds = {}

    for name, n_idx in occlusion_node_table.items():
        # read the bounds data from the extras
        bounds = np.array(ast.literal_eval(merged_file.nodes[n_idx].extras['bounds'])).reshape((2, 3))

        # copy that to the occlusion bounds table
        occlusion_bounds[n_idx] = bounds

        parent_node = merged_file.nodes[unit_node_table[merged_file.nodes[n_idx].extras["parent_unit"]]]
        parent_node.children.append(n_idx)

    import trimesh
    # each node in the mesh_node_table are assigned according to the occlusion bounds table
    for name, n_idx_list in mesh_node_table.items():
        for n_idx in n_idx_list:
            # get the position of the node from the matrix
            pos = np.array(merged_file.nodes[n_idx].matrix).reshape((4, 4))[3, :3]

            for b_idx, bounds in occlusion_bounds.items():
                if trimesh.bounds.contains(bounds, [pos]):
                    merged_file.nodes[b_idx].children.append(n_idx)
                    break

    # check that none of the nodes have intersecting children
    nodes_checked = set()
    nodes_checked.add(top_node_idx)

    # seems to be the top node + occlusion nodes + unit nodes. hmm...
    hmm = set()

    for n_idx, n in enumerate(merged_file.nodes):
        if len(n.children) == 0:
            hmm.add(n_idx)
            continue
        n.children = list(set(n.children))

        for c in n.children:
            if c in nodes_checked:
                breakpoint()
            else:
                nodes_checked.add(c)

    # check and fix textures/images/materials
    im_name_set = set(i.name for i in merged_file.images)
    tex_name_set = set(t.name for t in merged_file.textures)

    # this just means that there are images in the textures folder that are not used as a texture
    assert len(tex_name_set) < len(im_name_set)

    mats_blank = set()
    mats_with_unknown = {}
    mats_for_fixing = set()
    for mat in merged_file.materials:
        if len(mat.extras) == 0:
            mats_blank.add(mat.name)
            continue

        if "unknown" in mat.extras:
            mats_with_unknown[mat.name] = mat.extras["unknown"]
        if "specular" in mat.extras:
            mats_for_fixing.add(mat.name)
        if "blend" in mat.extras:
            mats_for_fixing.add(mat.name)

        diffuse_texture = mat.extras.get("diffuse")
        normal_texture = mat.extras.get("normal")

        if mat.pbrMetallicRoughness is not None:
            if diffuse_texture is not None:
                if len(diffuse_texture.split(",")) > 1:
                    mats_for_fixing.add(mat.name)

                mat.pbrMetallicRoughness.baseColorTexture.index = textures.get(diffuse_texture.split(",")[0])

        if mat.normalTexture is not None:
            if normal_texture is not None:
                if len(normal_texture.split(",")) > 1:
                    mats_for_fixing.add(mat.name)

                mat.normalTexture.index = textures.get(normal_texture)

    for tex in merged_file.textures:
        tex.source = [i.name for i in merged_file.images].index(tex.name)

    merged_file.save(outfile)


if __name__ == "__main__":
    merge_multinode_gltf(r"F:\Projects\pyDXHR\output\masterunit_gltf\det_city")
