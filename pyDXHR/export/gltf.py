"""
Convert section or DRM to GLTF files
"""

import shutil
import os
from copy import copy
import json
from tempfile import gettempdir
from pathlib import Path
from pyDXHR.DRM import DRM
from pyDXHR.DRM.Section import RenderMesh, Section, Material, RenderResource
from pyDXHR.export.mesh import MeshData
import pygltflib as gl
from dotenv import load_dotenv
load_dotenv()


def from_section(sec: Section, save_to: Path | str) -> None:
    """
    Convert a section to a single GLTF file
    """
    rm = RenderMesh.from_section(sec)
    name = sec.header.section_id
    breakpoint()


def from_drm(drm: DRM, save_to: Path | str,
             scale: float = 1.0,
             z_up: bool = False,
             optimize_for_lumen: bool = False) -> None:
    """
    Convert DRM to a single GLTF file. Not intended for unit DRMs.
    """
    rm_list = RenderMesh.from_drm(drm)
    mat_list = Material.from_drm(drm)
    tex_list = RenderResource.from_drm(drm)
    texture_dest_dir = Path(save_to).parent / "textures"
    texture_dest_dir.mkdir(parents=True, exist_ok=True)

    if drm.name:
        drm_name = Path(drm.name).stem
    else:
        drm_name = "DXHR DRM"

    # read material data
    for mat in mat_list:
        mat.read()

    # read texture data
    for tex in tex_list:
        image = tex.read()
        image.to_dds(save_to=texture_dest_dir)

    # generate MeshData
    gltf_list = []
    temp_dest_path = None
    temp_buffer_path = None
    for rm in rm_list:
        if rm is None:
            continue

        md = rm.parse_mesh_data()
        md.name = f"{rm.section_id:08X}"

        # save it to a temporary directory so that the buffer file will be created
        temp_dest_path = Path(gettempdir()) / f"{rm.section_id:08X}.gltf"
        temp_buffer_path = Path(gettempdir()) / f"{rm.section_id:08X}.bin"

        if bool(os.getenv("lumen", False)) or optimize_for_lumen:
            md.to_lumen_gltf(temp_dest_path)
        else:
            md.to_gltf(temp_dest_path)

        loaded_gltf = gl.GLTF2().load(temp_dest_path)
        loaded_gltf.nodes[0].name = f"N_{rm.section_id:08X}"
        gltf_list.append(loaded_gltf)

    if len(gltf_list) == 1:
        if temp_dest_path is not None:
            if temp_buffer_path.is_file():
                shutil.move(temp_buffer_path, Path(save_to).parent / (Path(save_to).stem + ".bin"))

            gltf_list[0].buffers[0].uri = Path(save_to).stem + ".bin"
            gltf_list[0].save(save_to)

    else:
        # merge the gltf if there's more than one
        merged_gltf = gl.GLTF2()
        merged_gltf.asset = MeshData.generate_asset_metadata()
        top_node = gl.Node(
            name=drm_name,
        )
        top_node.scale = [scale, scale, scale]
        if z_up:
            top_node.rotation = [0, 0, 1, 0]

        merged_gltf.nodes.append(top_node)

        merged_gltf.scenes.append(gl.Scene(name=drm_name, nodes=[0]))
        merged_gltf.scene = 0

        # materials and images
        compiled_materials = {
            m.name: copy(m)
            for f in gltf_list
            for m in f.materials
        }

        # the materials are just copied in bulk to the GLTF file
        merged_gltf.materials = list(compiled_materials.values())
        mat_id_list = list(compiled_materials.keys())
        # to get the mat index given a cdcMatID: mat_id_list.index(cdcMatID)

        mat_data = {f"M_{mat.section_id:08X}": mat.material_tex_list for mat in mat_list}
        for mat in merged_gltf.materials:
            if mat.name in mat_data:
                mat.extras = {}
                for mt in mat_data[mat.name]:
                    mat.extras |= mt.to_json()
                # mat.extras = list(set([f"{mt.texture_id:08X}" for mt in mat_data[mat.name]]))

        compiled_images = {
            i.name: copy(i)
            for f in gltf_list
            for i in f.images
        }

        # the URI attached to the image needs to be updated before it gets attached
        for im in compiled_images.values():
            merged_gltf.images.append(im)

        im_id_list = list(compiled_images.keys())

        # then the textures need to be copied
        if len([t for f in gltf_list for t in f.textures]) != 0:
            compiled_textures = {
                t.name: copy(t)
                for f in gltf_list
                for t in f.textures
            }

            merged_gltf.textures = list(compiled_textures.values())
            tex_id_list = list(compiled_textures.keys())
            assert len(im_id_list) == len(tex_id_list)

            for tex_name, gltf_tex in compiled_textures.items():
                gltf_tex.source = im_id_list.index(tex_name)

        empty_image_buffer = None
        empty_image_buffer_view = None

        buffer_uri_list = []
        for f in gltf_list:
            file_node = gl.Node(
                name=f.extras.get("MeshDataName")
            )
            current_node_index: int = len(merged_gltf.nodes)
            merged_gltf.nodes.append(file_node)
            top_node.children.append(current_node_index)

            empty_image_buffer_view_list = [(idx, bv) for idx, bv in enumerate(f.bufferViews) if bv.name == "empty"]
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

            if bool(os.getenv("lumen", False)):
                # original top node + mesh nodes
                assert len(f.nodes) - 1 == len(f.meshes)
            else:
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

                current_node_index: int = len(merged_gltf.nodes)
                merged_gltf.nodes.append(node)
                file_node.children.append(current_node_index)

                merged_gltf.meshes.append(mesh)

            buffer: gl.Buffer = copy(f.buffers[0])
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
            empty_img_idx, empty_img = [(idx, i) for idx, i in enumerate(merged_gltf.images) if i.name == "empty"][0]

            empty_image_buffer_view.buffer = len(merged_gltf.buffers)
            empty_img.bufferView = len(merged_gltf.bufferViews)

            merged_gltf.bufferViews.append(empty_image_buffer_view)
            merged_gltf.buffers.append(empty_image_buffer)
            empty_tex.source = empty_img_idx

        for b in buffer_uri_list:
            temp_buffer_path = Path(gettempdir()) / b
            shutil.move(temp_buffer_path, Path(save_to).parent / b)

        merged_gltf.save(save_to)

    # remove the temporary gltf
    os.remove(temp_dest_path)
