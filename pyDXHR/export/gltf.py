"""
Convert section or DRM to GLTF files
"""
import os
import tempfile
import shutil
from copy import copy
import json
from tempfile import gettempdir
from pathlib import Path
from typing import Optional, List, Dict

import kaitaistruct
import numpy as np

from pyDXHR.DRM import DRM
from pyDXHR.DRM.Section import RenderMesh, Section, Material, RenderResource
from pyDXHR.export.mesh import MeshData
import pygltflib as gl
from scipy.spatial.transform import Rotation

from dotenv import load_dotenv

load_dotenv()


def to_temp(sec: Section) -> Optional[gl.GLTF2]:
    temp_dir = Path(tempfile.gettempdir()) / "pyDXHR"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        rm = RenderMesh.from_section(sec)
    except kaitaistruct.KaitaiStructError:
        return None

    if rm is None:
        return None

    md = rm.parse_mesh_data()
    md.name = f"{sec.header.section_id:08X}"

    temp_dest_path = temp_dir / f"{rm.section_id:08X}.gltf"
    temp_buffer_path = temp_dir / f"{rm.section_id:08X}.bin"

    md.to_gltf(temp_dest_path)

    loaded_gltf = gl.GLTF2().load(temp_dest_path)
    loaded_gltf.nodes[0].name = f"SM_{rm.section_id:08X}"

    if len(loaded_gltf.accessors) == 0:
        return None

    return loaded_gltf


def from_section(sec: Section, save_to: Path | str) -> None:
    """
    Convert a section to a single GLTF file
    """
    try:
        rm = RenderMesh.from_section(sec)
    except kaitaistruct.KaitaiStructError:
        return None

    if rm is None:
        return None

    md = rm.parse_mesh_data()
    md.name = f"{sec.header.section_id:08X}"

    md.to_gltf(save_to)


def from_drm(
    drm: DRM,
    save_to: Path | str,
    scale: float = 1.0,
    z_up: bool = False,
    skip_textures: bool = False,
) -> None:
    """
    Convert DRM to a single GLTF file. Not intended for unit DRMs.
    """
    rm_list = RenderMesh.from_drm(drm)
    mat_list = Material.from_drm(drm)

    texture_dest_dir = Path(save_to).parent / "textures"
    if not skip_textures:
        tex_list = RenderResource.from_drm(drm)
        texture_dest_dir.mkdir(parents=True, exist_ok=True)
    else:
        tex_list = []

    if drm.name:
        drm_name = Path(drm.name).stem
    else:
        drm_name = "DXHR DRM"

    # read material data
    for mat in mat_list:
        mat.read()

    # read texture data
    # this for loop would not run if tex_list is empty anyway
    for tex in tex_list:
        im = tex.read()
        if os.getenv("texture_format") == "tga":
            im.to_tga(save_to=texture_dest_dir)
        elif os.getenv("texture_format") == "png":
            im.to_png(save_to=texture_dest_dir)
        else:
            im.to_dds(save_to=texture_dest_dir)

    # generate MeshData
    gltf_list = []
    temp_dest_path = None
    temp_buffer_path = None
    for rm in rm_list:
        if rm is None:
            continue

        md = rm.parse_mesh_data()
        # md.name = Path(rm.file_name).stem if rm.file_name is not None else f"{rm.section_id:08X}"
        md.name = f"{rm.section_id:08X}"
        md.set_material_data(mat_list)
        md.set_texture_data(tex_list)

        # save it to a temporary directory so that the buffer file will be created
        (Path(gettempdir()) / "pyDXHR").mkdir(parents=True, exist_ok=True)
        temp_dest_path = Path(gettempdir()) / "pyDXHR" / f"{rm.section_id:08X}.gltf"
        temp_buffer_path = Path(gettempdir()) / "pyDXHR" / f"{rm.section_id:08X}.bin"

        md.to_gltf(temp_dest_path)

        loaded_gltf = gl.GLTF2().load(temp_dest_path)
        loaded_gltf.nodes[0].name = f"SM_{rm.section_id:08X}"
        gltf_list.append(loaded_gltf)

    merge_gltf(
        gltf_list=gltf_list,
        save_to=save_to,
        mat_list=mat_list,
        tex_list=tex_list,
        drm_name=drm_name,
        scale=scale,
        z_up=z_up
    )


def merge_gltf(
    gltf_list: List[gl.GLTF2],
    save_to: str | Path,
    mat_list: Optional = None,
    tex_list: Optional = None,
    drm_name="DXHR DRM",
    scale=1.0,
    z_up=False,
):
    # merge the gltf if there's more than one
    merged_gltf = gl.GLTF2()
    merged_gltf.asset = MeshData.generate_asset_metadata()
    top_node = gl.Node(
        name=drm_name,
    )
    top_node.scale = [scale, scale, scale]
    if z_up:
        top_node.rotation = (
            Rotation.from_euler("x", -90, degrees=True).as_quat().tolist()
        )

    merged_gltf.nodes.append(top_node)

    merged_gltf.scenes.append(gl.Scene(name=drm_name, nodes=[0]))
    merged_gltf.scene = 0

    # materials and images
    compiled_materials = {m.name: copy(m) for f in gltf_list for m in f.materials}

    # the materials are just copied in bulk to the GLTF file
    merged_gltf.materials = list(compiled_materials.values())
    mat_id_list = list(compiled_materials.keys())
    # to get the mat index given a cdcMatID: mat_id_list.index(cdcMatID)

    mat_data = {f"M_{mat.section_id:08X}": mat.material_tex_list for mat in mat_list}
    for mat in merged_gltf.materials:
        if mat.name in mat_data:
            mat.extras = {}
            for md in mat_data[mat.name]:
                mat.extras |= md.to_json()
                # mat.extras["file_name"] = fn
            # mat.extras = list(set([f"{mt.texture_id:08X}" for mt in mat_data[mat.name]]))

    compiled_images = {i.name: copy(i) for f in gltf_list for i in f.images}

    # if the textures have filenames, it makes sense to attach the images to the GLTF
    # otherwise, they are kept in the textures folder
    has_named_textures = False
    if tex_list is not None and len(tex_list):
        if tex_list[0].file_name is not None:
            has_named_textures = True
            textures_dir = Path(save_to).parent / "textures"
            textures_dir.mkdir(parents=True, exist_ok=True)

            for tex in tex_list:
                im = tex.read()
                if os.getenv("texture_format") == "tga":
                    im.to_tga(save_to=textures_dir)
                elif os.getenv("texture_format") == "png":
                    im.to_png(save_to=textures_dir)
                else:
                    im.to_dds(save_to=textures_dir)

    # the URI attached to the image needs to be updated before it gets attached
    for im in compiled_images.values():
        merged_gltf.images.append(im)

    im_id_list = list(compiled_images.keys())

    # then the textures need to be copied
    if len([t for f in gltf_list for t in f.textures]) != 0:
        compiled_textures = {t.name: copy(t) for f in gltf_list for t in f.textures}

        merged_gltf.textures = list(compiled_textures.values())
        tex_id_list = list(compiled_textures.keys())
        assert len(im_id_list) == len(tex_id_list)

        for tex_name, gltf_tex in compiled_textures.items():
            gltf_tex.source = im_id_list.index(tex_name)

    if has_named_textures:
        # add the texlist as images/textures
        image_index_dict = {}
        for tex in tex_list:
            gl_im = gl.Image(
                uri="textures/" + tex.resource_name + "." + os.getenv("texture_format", "dds"),
                name=tex.resource_name,
                extras={
                    "cdcTextureId": f"{tex.section_id:08X}",
                }
            )
            image_index_dict[f"{tex.section_id:08X}"] = len(merged_gltf.images)

            gl_tex = gl.Texture(
                name=tex.resource_name,
                source=len(merged_gltf.images),
                extras={
                    "cdcTextureId": f"{tex.section_id:08X}",
                }
            )

            merged_gltf.images.append(gl_im)
            merged_gltf.textures.append(gl_tex)

        for idx, mat in enumerate(merged_gltf.materials):
            mat_name = [Path(m.file_name).stem for m in mat_list if int(mat.name.split("_")[1], 16) == m.section_id][0]
            mat.name = mat_name
            for tex_id, mat_data in mat.extras.items():
                tex_name_matches = [Path(t.file_name).stem for t in tex_list if int(tex_id, 16) == t.section_id]
                if len(tex_name_matches):
                    tex_name = tex_name_matches[0]
                else:
                    continue

                if "normal" in tex_name or tex_name.endswith("_n"):
                    norm = gl.NormalMaterialTexture(
                        index=image_index_dict[tex_id],
                    )

                    mat.normalTexture = norm

                if "flat" in tex_name or "diffuse" in tex_name or tex_name.endswith("_d"):
                    pbr = gl.PbrMetallicRoughness(
                        baseColorTexture=gl.TextureInfo(
                           index=image_index_dict[tex_id],
                        )
                    )

                    mat.pbrMetallicRoughness = pbr

    empty_image_buffer = None
    empty_image_buffer_view = None

    buffer_uri_list = []
    for f in gltf_list:
        current_node_index: int = len(merged_gltf.nodes)

        empty_image_buffer_view_list = [
            (idx, bv) for idx, bv in enumerate(f.bufferViews) if bv.name == "empty"
        ]
        if len(empty_image_buffer_view_list) == 1:
            (
                empty_image_bv_index,
                empty_image_buffer_view,
            ) = empty_image_buffer_view_list[0]
            f.bufferViews.pop(empty_image_bv_index)
        else:
            continue
            # breakpoint()

        if len(f.buffers) == 2:
            empty_image_buffer = copy(f.buffers[1])
            f.buffers.pop(1)

        assert len(f.accessors) == len(f.bufferViews)
        assert len(f.buffers) == 1

        assert len(f.nodes) == 1
        assert len(f.meshes) == 1

        if f.buffers[0].byteLength == 0:
            continue

        mesh_nodes = [n for n in f.nodes if not len(n.children)]
        assert len(mesh_nodes) == len(f.meshes)

        node: gl.Node
        mesh: gl.Mesh
        for node, mesh in zip(mesh_nodes, f.meshes):
            mesh = copy(mesh)
            node = copy(node)
            node.mesh = len(merged_gltf.meshes)
            node.rotation = None
            node.scale = None

            current_node_index: int = len(merged_gltf.nodes)
            merged_gltf.nodes.append(node)
            top_node.children.append(current_node_index)

            merged_gltf.meshes.append(mesh)

        buffer: gl.Buffer = copy(f.buffers[0])
        if buffer.byteLength == 0:
            breakpoint()
        buffer_uri_list.append(buffer.uri)

        acc_cursor = len(merged_gltf.accessors)
        for o_acc, o_bv in zip(f.accessors, f.bufferViews):
            acc = copy(o_acc)
            bv = copy(o_bv)

            bv.buffer = len(merged_gltf.buffers)
            acc.bufferView += acc_cursor

            merged_gltf.accessors.append(acc)
            merged_gltf.bufferViews.append(bv)

        merged_gltf.buffers.append(buffer)

        for mesh in f.meshes:
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
                prim.material = mat_id_list.index(f"M_{cdc_mat_id}")

    if empty_image_buffer_view is not None and empty_image_buffer is not None:
        empty_tex = [t for t in merged_gltf.textures if t.name == "empty"][0]
        empty_img_idx, empty_img = [
            (idx, i) for idx, i in enumerate(merged_gltf.images) if i.name == "empty"
        ][0]

        empty_image_buffer_view.buffer = len(merged_gltf.buffers)
        empty_img.bufferView = len(merged_gltf.bufferViews)

        merged_gltf.bufferViews.append(empty_image_buffer_view)
        merged_gltf.buffers.append(empty_image_buffer)
        empty_tex.source = empty_img_idx

    temp_dir = Path(tempfile.gettempdir()) / "pyDXHR"
    temp_dir.mkdir(parents=True, exist_ok=True)

    for b in buffer_uri_list:
        temp_buffer_path = Path(temp_dir) / b
        shutil.move(temp_buffer_path, Path(save_to).parent / b)

    shutil.rmtree(temp_dir)
    merged_gltf.save(save_to)


def merge_using_library(
    library_path: str | Path,
    loc_table: Dict[str | int, List[np.ndarray]],
    save_to: str | Path,
    unit_name: str = "DXHR",
    scale=1.0,
    z_up=False,
):
    merged_gltf = gl.GLTF2()
    merged_gltf.asset = MeshData.generate_asset_metadata()
    top_node = gl.Node(
        name=unit_name,
    )
    top_node.scale = [scale, scale, scale]
    if z_up:
        top_node.rotation = (
            Rotation.from_euler("x", -90, degrees=True).as_quat().tolist()
        )

    merged_gltf.nodes.append(top_node)

    merged_gltf.scenes.append(gl.Scene(name=unit_name, nodes=[0]))
    merged_gltf.scene = 0

    empty_buffer = None
    empty_bv = None

    # copy the materials
    for path in loc_table.keys():
        if isinstance(path, int):
            path = f"{path:08X}"

        try:
            loaded_gltf = gl.GLTF2().load(
                library_path / (Path(path).name.replace(".drm", "") + ".gltf")
            )
        except FileNotFoundError:
            continue

        if empty_buffer is None and empty_bv is None and len(loaded_gltf.buffers):
            empty_buffer = [b for b in loaded_gltf.buffers if b.extras.get("name") == "empty"][0]
            empty_bv = [bv for bv in loaded_gltf.bufferViews if bv.name == "empty"][0]
        for mat in loaded_gltf.materials:
            if mat not in merged_gltf.materials:
                merged_gltf.materials.append(mat)

    # remove duplicates
    clean_loc_table = {
        k if isinstance(k, str) else f"{k:08X}": set() for k in loc_table.keys()
    }
    for k, vl in loc_table.items():
        if isinstance(k, int):
            k = f"{k:08X}"

        for v in vl:
            tup = tuple(np.round(v, 2).T.flatten().tolist())
            clean_loc_table[k].add(tup)

    for path, trs_list in clean_loc_table.items():
        try:
            loaded_gltf = gl.GLTF2().load(
                library_path / (Path(path).name.replace(".drm", "") + ".gltf")
            )
        except FileNotFoundError:
            continue

        # if len(loaded_gltf.nodes) > 1:
        #     breakpoint()
        #     # print(path)
        #     continue
        # elif len(loaded_gltf.meshes) == 0:
        #     continue
        # else:
        #     assert len(loaded_gltf.meshes) == 1

        if len(loaded_gltf.meshes) == 0:
            continue

        for m_idx, m in enumerate(loaded_gltf.meshes):
            mesh = copy(m)
            current_mesh_number = len(merged_gltf.meshes)
            merged_gltf.meshes.append(mesh)

            # get the acc/bv for this particular mesh
            mesh_acc = [
                acc
                for acc in loaded_gltf.accessors
                if acc.extras.get("MESH_NAME") == mesh.name
            ]
            mesh_bv = [
                bv
                for bv in loaded_gltf.bufferViews
                if bv.extras.get("MESH_NAME") == mesh.name
            ]
            mesh_buffers = [
                b for b in loaded_gltf.buffers if b.extras.get("name") == mesh.name
            ]

            # copy accessors and buffer views
            acc_cursor = len(merged_gltf.accessors)

            # if m_idx == 0, then this does nothing, it's just zero
            # but if m_idx > 0, then this subtracts the current value of the BV from the first mesh
            # because the BV index of the first mesh needs to be "pushed back"
            # uh... it works.
            acc_start_for_mdx_1 = mesh_acc[0].bufferView
            if m_idx > 0:
                for acc in mesh_acc:
                    acc.bufferView -= acc_start_for_mdx_1

            for o_acc, o_bv in zip(mesh_acc, mesh_bv):
                acc = copy(o_acc)
                bv = copy(o_bv)

                bv.buffer = len(merged_gltf.buffers)
                bv.name = None
                acc.name = None
                acc.bufferView += acc_cursor

                merged_gltf.accessors.append(acc)
                merged_gltf.bufferViews.append(bv)

            # copy buffers
            for b in mesh_buffers:
                b.uri = "library/" + b.uri
                merged_gltf.buffers.append(b)

            prim: gl.Primitive
            for prim in mesh.primitives:
                attribute_dict = json.loads(prim.attributes.to_json())
                revised_attrs = {
                    attr: attr_idx + acc_cursor - acc_start_for_mdx_1
                    for attr, attr_idx in attribute_dict.items()
                    if attr_idx is not None
                }

                prim.attributes = gl.Attributes(**revised_attrs)
                prim.indices += acc_cursor - acc_start_for_mdx_1

                cdc_mat_id = "M_" + prim.extras["cdcMatID"].upper()
                prim.material = [mat.name for mat in merged_gltf.materials].index(
                    cdc_mat_id
                )

            # take the nodes of the loaded gltf that have no children
            gltf_nodes = [n for n in loaded_gltf.nodes if n.name == "SM_" + mesh.name]
            assert len(gltf_nodes) == 1
            for trs in trs_list:
                node = copy(gltf_nodes[0])

                node.matrix = trs
                node.translation = None
                node.rotation = None
                node.scale = None
                node.mesh = current_mesh_number

                merged_gltf.nodes.append(node)
                top_node.children.append(len(merged_gltf.nodes) - 1)

    # add empty texture for the materials
    if empty_buffer is not None and empty_bv is not None:
        empty_bv.buffer = len(merged_gltf.buffers)
        merged_gltf.buffers.append(empty_buffer)

        empty_tex = gl.Texture(name="empty")
        empty_tex.source = 0
        merged_gltf.textures.append(empty_tex)

        empty_image = gl.Image(name="empty")
        empty_image.bufferView = len(merged_gltf.bufferViews)
        empty_image.mimeType = "image/png"
        merged_gltf.images.append(empty_image)

        merged_gltf.bufferViews.append(empty_bv)

        for mat in merged_gltf.materials:
            mat.pbrMetallicRoughness = gl.PbrMetallicRoughness(
                baseColorTexture=gl.TextureInfo(index=0)
            )

    merged_gltf.save(save_to)


def merge_all(
        save_to: str | Path,
        gltf_files: List[str | Path],
        drm_name="DXHR DRM",
        scale=1.0,
        z_up=False,
):
    merged_gltf = gl.GLTF2()
    merged_gltf.asset = MeshData.generate_asset_metadata()
    top_node = gl.Node(
        name=drm_name,
    )
    top_node.scale = [scale, scale, scale]
    if z_up:
        top_node.rotation = (
            Rotation.from_euler("x", -90, degrees=True).as_quat().tolist()
        )

    merged_gltf.nodes.append(top_node)

    merged_gltf.scenes.append(gl.Scene(name=drm_name, nodes=[0]))
    merged_gltf.scene = 0

    for file in gltf_files:
        loaded_gltf = gl.GLTF2().load(file)


    breakpoint()


    merged_gltf.save(save_to)