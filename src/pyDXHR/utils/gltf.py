import os
from pathlib import Path
import pygltflib as gltf
from typing import List, Optional, Tuple, Dict, Final
import numpy as np
import warnings
import itertools
import shutil

from pyDXHR.cdcEngine.DRM.Sections.Material import Material, guess_materials
from pyDXHR.cdcEngine.DRM.Sections import RenderResource
from pyDXHR.utils.MeshData import MeshData, VertexSemantic

GLTF_SCALE: Final[float] = 0.002


def build_gltf(mesh_data: MeshData,
               save_to: Optional[str | Path] = None,
               name: Optional[str] = None,
               as_bytes: bool = False,
               share_textures: bool = True,
               apply_scale: bool = False,
               scale: float = 1.0,
               blank_materials: bool = False,
               ):
    """
    "share_textures": will create a folder called "textures"
    "blank materials": create the materials, but do not assign textures
    """
    if apply_scale:
        scale = GLTF_SCALE

    # region setup
    asset_data = gltf.Asset()
    asset_data.generator = "pyDXHR"
    asset_data.version = "2.0"
    asset_data.copyright = "2011 (c) Eidos Montreal"

    gltf_root = gltf.GLTF2()

    binary_blob: bytes = b''

    parent_node = gltf.Node(name=name)
    parent_node_index = _add_to_gltf(gltf_root, parent_node)
    # parent_node.scale = 3 * [scale]

    scene_node = gltf.Scene()
    scene_node.nodes = [parent_node_index]
    scene_index = _add_to_gltf(gltf_root, scene_node)
    gltf_root.scene = scene_index

    mesh = gltf.Mesh(name=name)
    mesh_index = _add_to_gltf(gltf_root, mesh)
    parent_node.mesh = mesh_index
    # endregion

    # region create materials
    complete_image_dict = {}
    mat_index_dict: Dict[Material, int] = {}
    for mat_index, mat in enumerate(mesh_data.MaterialIDList):
        if mat not in mat_index_dict:
            image_dict = _populate_material(gltf_root, mat.ID, blank_materials=blank_materials)
            mat_index_dict[mat] = mat_index
            complete_image_dict |= image_dict
        else:
            continue
    #
    # # this part rearranges the materials in the GLTF materials list such that the "_1" materials float to the top
    # # so that the mesh primitives will know which materials to use. the "_2" materials should be left unused
    # # the only reason why the "_2" materials exist is so that their textures can be included in the final GLTF file
    # # because i dont think GLTF supports "dangling" images like in blender and i still have no idea how to do
    # # auto-texturing/auto-UV assignments. it would be nice tho...
    # mats = []
    # end_mats = []
    # for m in gltf_root.materials:
    #     if m.name.endswith("_1"):
    #         mats.append(m)
    #     else:
    #         end_mats.append(m)
    #
    # mats.extend(end_mats)
    # gltf_root.materials = mats
    # # endregion

    # region vertex
    for idx, (_, vtx_sem_dict) in enumerate(mesh_data.VertexBuffers.items()):
        attribute_index_dict = {k.value: None for k in VertexSemantic}

        for vtx_sem, array in vtx_sem_dict.items():
            vtx_buffer_view, vtx_accessor, vtx_byte_data = _add_vertex_data(
                vtx_sem=vtx_sem,
                vtx_array=array,
                binary_blob=binary_blob,
                mesh_num=idx,
                scale=scale)

            binary_blob += vtx_byte_data
            vtx_buffer_view_index = _add_to_gltf(gltf_root=gltf_root, item=vtx_buffer_view)
            vtx_accessor.bufferView = vtx_buffer_view_index
            attribute_index_dict[vtx_sem.value] = vtx_buffer_view_index

            _ = _add_to_gltf(gltf_root=gltf_root, item=vtx_accessor)

        mesh_attributes = _populate_mesh_attributes(attribute_index_dict)

        mesh_prim_list: List[Tuple[Material, np.ndarray]] = mesh_data.MeshPrimIndexed[idx]

        for imp, (mat, arr) in enumerate(mesh_prim_list):
            accessor_index = len(gltf_root.accessors)

            idx_buffer_view, idx_accessor, idx_byte_data = _add_index_data(
                array=arr,
                binary_blob=binary_blob,
                mesh_num=idx,
                submesh_num=imp
            )

            binary_blob += idx_byte_data
            idx_buffer_view_index = _add_to_gltf(gltf_root=gltf_root, item=idx_buffer_view)
            idx_accessor.bufferView = idx_buffer_view_index
            _ = _add_to_gltf(gltf_root=gltf_root, item=idx_accessor)

            mesh_prim = gltf.Primitive(
                attributes=mesh_attributes,
                indices=accessor_index,
                material=mat_index_dict[mat]
            )

            mesh.primitives.append(mesh_prim)
    # endregion

    # region closing
    _create_buffer(gltf_root, binary_blob)

    if save_to:
        save_to = Path(save_to)
        if save_to.suffix == ".gltf":
            file_destination = save_to
        else:
            file_destination = save_to.parent / (save_to.name + '.gltf')

        if share_textures:
            # creates a folder called textures where the files will be copied
            (file_destination.parent / "textures").mkdir(parents=True, exist_ok=True)
            texture_destination = "textures"
        else:
            # creates a folder with the same name as the input
            (file_destination.parent / file_destination.name).mkdir(parents=True, exist_ok=True)
            texture_destination = file_destination.name
        _copy_texture_images(image_dict=complete_image_dict,
                             relative_texture_destination=texture_destination,
                             absolute_destination=file_destination)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            gltf_root.save(file_destination, asset=asset_data)

    if as_bytes:
        return b"".join(gltf_root.save_to_bytes())
    else:
        return gltf_root
    # endregion


def _copy_texture_images(
        image_dict: Dict[int, gltf.Image],
        relative_texture_destination: str,
        absolute_destination: Path
):
    pydxhr_texlib = os.getenv('PYDXHR_TEXLIB')

    if not pydxhr_texlib:
        raise Exception
    else:
        for image_index, gltf_image in image_dict.items():
            tex_id = gltf_image.extras["cdcTextureID"]
            img_as_path = RenderResource.from_library(tex_id, pydxhr_texlib, as_path=True)
            shutil.copy(img_as_path, absolute_destination.parent / relative_texture_destination)
            gltf_image.uri = str(Path(relative_texture_destination) / img_as_path.name)
            gltf_image.name = "T_" + f"{tex_id:x}".rjust(8, '0')
            gltf_image.mimeType = "image/png"


def _populate_material(
        gltf_root: gltf.GLTF2,
        cdc_material_id: int,
        blank_materials: bool = False
):

    pydxhr_matlib = os.getenv('PYDXHR_MATLIB')

    def _add_image():
        img = gltf.Image(
            name="I_" + f"{tx_id:x}".rjust(8, '0'),
            extras={
                "cdcTextureID": tx_id,
                "guessed_key": mat_key,
                "cdcMaterialID": cdc_material_id
            }
        )
        gltf_im_id = _add_to_gltf(gltf_root, img)

        if blank_materials:
            return None
        # the images are added to the gltf image list regardless if they'll be used later on
        # so that the textures directory will be created and they'll still be saved there

        image_dict[gltf_im_id] = img

        tx = gltf.Texture(
            source=gltf_im_id,
            name="T_" + f"{tx_id:x}".rjust(8, '0'),
            extras={
                "cdcTextureID": tx_id,
                "guessed_key": mat_key,
                "cdcMaterialID": cdc_material_id
            }
        )
        return _add_to_gltf(gltf_root, tx)

    if not pydxhr_matlib:
        raise Exception
    else:
        mat_name = "M_" + f"{cdc_material_id:x}".rjust(8, '0')

        arr = np.loadtxt(pydxhr_matlib, delimiter=",", dtype=int)
        tex_arr = arr[np.where(arr[:, 0] == cdc_material_id)]

        seen = []
        materials = {}
        for tex_id, tex_info in zip(tex_arr[:, 1], tex_arr[:, 2:]):
            if tex_id in seen:
                continue

            mat_type = guess_materials(*tex_info)

            if mat_type not in materials:
                materials[mat_type] = []
            materials[mat_type].append(tex_id.item())

            seen.append(tex_id.item())

        # len_mats = max(len(images) for images in materials.values())
        materials_fixed = [dict(zip(materials, t)) for t in itertools.zip_longest(*materials.values())]
        # image_list = list(itertools.chain.from_iterable(materials.values()))

        image_dict: Dict[int, gltf.Image] = {}
        for i, mat in enumerate(materials_fixed):
            gltf_mat = gltf.Material(name=f"{mat_name}")
            if i == 0:
                for mat_key, tx_id in mat.items():
                    if not tx_id:
                        continue

                    gltf_tx_id = _add_image()
                    if gltf_tx_id:
                        tf = gltf.TextureInfo(index=gltf_tx_id)

                        match mat_key:
                            case "diffuse":
                                gltf_mat.pbrMetallicRoughness = gltf.PbrMetallicRoughness(baseColorTexture=tf)
                            case "normal":
                                gltf_mat.normalTexture = gltf.NormalMaterialTexture(index=gltf_tx_id)
                            case "blend":
                                pass
                            case _:
                                pass
                _add_to_gltf(gltf_root, gltf_mat)
            else:  # add dangling images + textures, but not attach to any materials - these can be fixed later, depending on the settings of the GLTF importer
                for mat_key, tx_id in mat.items():
                    if not tx_id:
                        continue

                    _ = _add_image()

        return image_dict


def _add_index_data(
        array: np.ndarray,
        binary_blob: bytes,
        mesh_num: int = -1,
        submesh_num: int = -1
) -> Tuple[gltf.BufferView, gltf.Accessor, bytes]:
    current_byte_offset = len(binary_blob)

    byte_data = array.flatten().tobytes()
    view = gltf.BufferView(
        buffer=0,
        byteOffset=current_byte_offset,
        byteLength=len(byte_data),
        target=gltf.ELEMENT_ARRAY_BUFFER,
        name=f"Mesh_{mesh_num}_Prim_{submesh_num}_indices"
    )

    accessor = gltf.Accessor(
        componentType=gltf.UNSIGNED_INT,
        count=array.size,
        type=gltf.SCALAR,
        max=[int(array.max())],
        min=[int(array.min())],
        name=f"Mesh_{mesh_num}_Prim_{submesh_num}_indices"
    )

    return view, accessor, byte_data


def _populate_mesh_attributes(attribute_index_dict: dict) -> gltf.Attributes:
    """
    Transforms a dictionary of attribute indices to the GLTF Attribute object

    :param attribute_index_dict:
    :return:
    """
    return gltf.Attributes(
        POSITION=attribute_index_dict[VertexSemantic.Position.value],
        NORMAL=attribute_index_dict[VertexSemantic.Normal.value],
        TANGENT=attribute_index_dict[VertexSemantic.Tangent.value],

        # I think HR only uses 1 and 2, but just in case...
        TEXCOORD_0=attribute_index_dict[VertexSemantic.TexCoord1.value],
        TEXCOORD_1=attribute_index_dict[VertexSemantic.TexCoord2.value],
        TEXCOORD_2=attribute_index_dict[VertexSemantic.TexCoord3.value],
        TEXCOORD_3=attribute_index_dict[VertexSemantic.TexCoord4.value],

        COLOR_0=attribute_index_dict[VertexSemantic.Color1.value],
        COLOR_1=attribute_index_dict[VertexSemantic.Color2.value],

        # not implemented
        JOINTS_0=None,
        WEIGHTS_0=None,

        # included in file for archival purposes
        _BINORMAL=attribute_index_dict[VertexSemantic.Binormal.value],
        _NORMAL2=attribute_index_dict[VertexSemantic.Normal2.value],  # so confused
        _PACKED_NTB=attribute_index_dict[VertexSemantic.PackedNTB.value],
    )


def _add_vertex_data(
        vtx_sem: VertexSemantic,
        vtx_array: np.ndarray,
        binary_blob: bytes,
        mesh_num: int = -1,
        scale: float = 1.0,
) -> Tuple[gltf.BufferView, gltf.Accessor, bytes]:
    """
    Transforms a vertex semantic/vertex numpy array to a GLTF bufferview + Accessor + byte data

    :param vtx_sem:
    :param vtx_array:
    :param binary_blob:
    :param mesh_num:
    :return:
    """
    if vtx_sem.value in VertexSemantic.tangents():
        vtx_array = add_tangent_handedness(vtx_array)

    elif vtx_sem.value in VertexSemantic.colors():
        # I'm not sure if this is correct, but if it gets the GLTF validator to shut up...
        vtx_array = np.abs(vtx_array)

    elif vtx_sem.value == VertexSemantic.Position.value:
        vtx_array *= scale

    current_byte_offset = len(binary_blob)
    byte_data = vtx_array.tobytes()

    view = gltf.BufferView(
        buffer=0,
        byteOffset=current_byte_offset,
        byteLength=len(byte_data),
        target=gltf.ARRAY_BUFFER,
        name=f"Mesh_{mesh_num}_{vtx_sem.name}"
    )

    accessor = gltf.Accessor(
        componentType=gltf.FLOAT,
        count=len(vtx_array),
        # max=[round(i, 2) for i in np.max(v, axis=0).tolist()],
        # min=[round(i, 2) for i in np.min(v, axis=0).tolist()],
        name=f"Mesh_{mesh_num}_{vtx_sem.name}"
    )

    if vtx_sem.value in VertexSemantic.tex_coords():
        accessor.type = gltf.VEC2
    elif vtx_sem.value in VertexSemantic.tangents():
        accessor.type = gltf.VEC4
    elif vtx_sem.value in VertexSemantic.normals():
        accessor.type = gltf.VEC3
    elif vtx_sem.value is VertexSemantic.Position.value:
        accessor.type = gltf.VEC3
        accessor.min = [round(i) - 1 for i in np.min(vtx_array, axis=0).tolist()]
        accessor.max = [round(i) + 1 for i in np.max(vtx_array, axis=0).tolist()]
    else:
        accessor.type = gltf.VEC3

    return view, accessor, byte_data


def _add_to_gltf(gltf_root: gltf.GLTF2, item: gltf.Property) -> int:
    """
    Adds a GLTF property to the GLTF object according to its type and returns the index of the property

    :param gltf_root:
    :param item:
    :return:
    """
    li: List[gltf.Property]
    match type(item).__qualname__:
        case gltf.Node.__qualname__:
            li = gltf_root.nodes
        case gltf.Mesh.__qualname__:
            li = gltf_root.meshes
        case gltf.Material.__qualname__:
            li = gltf_root.materials
        case gltf.Accessor.__qualname__:
            li = gltf_root.accessors
        case gltf.BufferView.__qualname__:
            li = gltf_root.bufferViews
        case gltf.Image.__qualname__:
            li = gltf_root.images
        case gltf.Scene.__qualname__:
            li = gltf_root.scenes
        case gltf.Texture.__qualname__:
            li = gltf_root.textures
        case _:
            raise KeyError

    index = len(li)
    li.append(item)
    return index


def _create_buffer(gltf_root: gltf.GLTF2, binary_blob: bytes) -> None:
    """
    Generates a buffer for binary blob and attaches it to the GLTF root

    :param gltf_root:
    :param binary_blob:
    :return:
    """

    buffer = gltf.Buffer()
    buffer.byteLength = len(binary_blob)
    gltf_root.buffers.append(buffer)

    gltf_root.set_binary_blob(binary_blob)


def add_tangent_handedness(v: np.ndarray, reverse: bool = False) -> np.ndarray:
    """
    See GLTF spec

    :param v:
    :param reverse:
    :return:
    """
    handedness = 1 if not reverse else -1
    return np.hstack([v, handedness*np.ones((1, v.shape[0])).T])
