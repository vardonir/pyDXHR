import os
from pathlib import Path
import pygltflib as gltf
from typing import List, Optional, Tuple, Dict
import numpy as np
import warnings
import shutil

from pyDXHR.cdcEngine.Sections.Material import Material
from pyDXHR.cdcEngine.Sections import RenderResource
from pyDXHR.utils.MeshData import MeshData, VertexSemantic


def build_gltf(mesh_data: MeshData,
               **kwargs,
               ):
    """
    "share_textures": will create a folder called "textures"
    "blank materials": create the materials, but do not assign textures
    """
    save_to = kwargs.get("save_to", None)
    name = kwargs.get("name", None)
    blank_materials = kwargs.get("blank_materials", False)
    skip_materials = kwargs.get("skip_materials", False)
    share_textures = kwargs.get("share_textures", True)
    as_bytes = kwargs.get("as_bytes", False)
    trimesh_post_processing = kwargs.get("trimesh_post_processing", False)

    # region setup
    asset_data = gltf.Asset()
    asset_data.generator = "pyDXHR"
    asset_data.version = "2.0"
    asset_data.copyright = "2011 (c) Eidos Montreal"

    gltf_root = gltf.GLTF2()
    from . import black_image_as_gltf_buffer

    # create the empty image + texture and add it to the gltf
    empty_image_buffer = black_image_as_gltf_buffer()

    empty_image = gltf.Image(
        name="dummyblack",
        mimeType="image/png",
    )

    empty_image_index = _add_to_gltf(gltf_root, empty_image)
    empty_texture = gltf.Texture(
        source=empty_image_index,
        name="dummyblack",
    )
    empty_texture_index = _add_to_gltf(gltf_root, empty_texture)

    binary_blob: bytes = b''

    parent_node = gltf.Node(name=name)
    parent_node_index = _add_to_gltf(gltf_root, parent_node)

    scene_node = gltf.Scene()
    scene_node.nodes = [parent_node_index]
    scene_index = _add_to_gltf(gltf_root, scene_node)
    gltf_root.scene = scene_index

    mesh = gltf.Mesh(
        name=name
    )
    mesh_index = _add_to_gltf(gltf_root, mesh)
    parent_node.mesh = mesh_index
    # endregion

    # region create materials
    complete_image_dict = {}
    mat_index_dict: Dict[Material, int] = {}
    if mesh_data.MaterialIDList:
        for mat_index, mat in enumerate(mesh_data.MaterialIDList):
            if mat not in mat_index_dict:
                image_dict = _populate_material(
                    gltf_root=gltf_root,
                    cdc_material_id=mat.ID,
                    empty_texture_index=empty_texture_index,
                    blank_materials=blank_materials,
                    skip_materials=skip_materials
                )

                mat_index_dict[mat] = mat_index
                complete_image_dict |= image_dict
            else:
                continue
    # TODO:
    #      console version - materials are in a separate section

    # endregion

    # region vertex
    for idx, (_, vtx_sem_dict) in enumerate(mesh_data.VertexBuffers.items()):
        attribute_index_dict = {k.value: None for k in VertexSemantic}

        for vtx_sem, array in vtx_sem_dict.items():
            vtx_buffer_view, vtx_accessor, vtx_byte_data = _add_vertex_data(
                vtx_sem=vtx_sem,
                vtx_array=array,
                binary_blob=binary_blob,
                mesh_num=idx,
                name=name,
            )

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
                submesh_num=imp,
                name=name
            )

            binary_blob += idx_byte_data
            idx_buffer_view_index = _add_to_gltf(gltf_root=gltf_root, item=idx_buffer_view)
            idx_accessor.bufferView = idx_buffer_view_index
            _ = _add_to_gltf(gltf_root=gltf_root, item=idx_accessor)

            mesh_prim = gltf.Primitive(
                attributes=mesh_attributes,
                indices=accessor_index,
                material=mat_index_dict.get(mat),
                extras={
                    "MESH_NAME": name,
                    "MESH_IDX": idx,
                    "PRIM_IDX": imp,
                    "cdcMatID": mat.Name,
                }
            )

            mesh.primitives.append(mesh_prim)
    # endregion

    # region closing
    _create_buffer(gltf_root, binary_blob, name)

    empty_image_buffer_view = gltf.BufferView(
        name="dummyblack",
        buffer=1,
        byteLength=empty_image_buffer.byteLength
    )
    empty_image_buffer_view_index = _add_to_gltf(gltf_root, empty_image_buffer_view)
    empty_image.bufferView = empty_image_buffer_view_index

    gltf_root.buffers.append(empty_image_buffer)

    if trimesh_post_processing:
        gltf_root = _trimesh_post_process(gltf_root)

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


def _trimesh_post_process(gltf_root: gltf.GLTF2):
    """ run some post-processing on the resulting GLTF file using trimesh """
    import trimesh
    from io import BytesIO

    # convert the GLTF file to a trimesh object
    gltf_binary = b"".join(gltf_root.save_to_bytes())
    gltf_trimesh = trimesh.load(BytesIO(gltf_binary), file_type="glb", force="mesh")

    # run the post-processing
    gltf_trimesh = gltf_trimesh.process()

    # convert the trimesh object back to a GLTF object instance
    export_blob = gltf_trimesh.export(file_type="glb")

    # load the GLTF object instance and return it back
    return gltf.GLTF2.load_from_bytes(export_blob)


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
            gltf_image.uri = "/".join((Path(relative_texture_destination) / img_as_path.name).parts)
            gltf_image.name = "T_" + f"{tex_id:x}".rjust(8, '0')
            gltf_image.mimeType = "image/png"


def _populate_material(
        gltf_root: gltf.GLTF2,
        empty_texture_index: int,
        cdc_material_id: int,
        blank_materials: bool = False,
        skip_materials: bool = False,
):
    import json
    mat_name = "M_" + f"{cdc_material_id:x}".rjust(8, '0')

    pydxhr_matlib = os.getenv('PYDXHR_MATLIB')
    if pydxhr_matlib is None:
        skip_materials = True

    if skip_materials:
        gltf_mat = gltf.Material(
            name=f"{mat_name}",
            extras={},
            alphaCutoff=None
        )

        _add_to_gltf(gltf_root, gltf_mat)
        return {}

    with open(Path(pydxhr_matlib) / "mtl_lib_v2.json", 'r') as f:
        mtl_lib = json.load(f)
    with open(Path(pydxhr_matlib) / "mtl_lib_for_checking.json", 'r') as f:
        inc_mtl_lib = json.load(f)

    def _add_image(tx_id: int, ignore_mat_key: bool = False):
        if tx_id in tx_dict:
            return tx_dict[tx_id]

        img = gltf.Image(
            name="I_" + f"{tx_id:x}".rjust(8, '0'),
            extras={
                "cdcTextureID": tx_id,  # keep this as a decimal int, used to get the image from the library
                "guessed_key": None if ignore_mat_key else mat_key,
                "cdcMaterialID": "M_" + f"{cdc_material_id:x}".rjust(8, '0')
            }
        )
        gltf_im_id = _add_to_gltf(gltf_root, img)
        image_dict[gltf_im_id] = img

        if blank_materials:
            return None
        # the images are added to the gltf image list regardless if they'll be used later on
        # so that the textures directory will be created and they'll still be saved there

        gltf_tx = gltf.Texture(
            source=gltf_im_id,
            name="T_" + f"{tx_id:x}".rjust(8, '0'),
            extras={
                "cdcTextureID": tx_id,
                "guessed_key": mat_key,
                "cdcMaterialID": "M_" + f"{cdc_material_id:x}".rjust(8, '0')
            }
        )
        gltf_txid = _add_to_gltf(gltf_root, gltf_tx)
        return gltf_txid

    if blank_materials:
        gltf_mat = gltf.Material(name=f"{mat_name}")
        _add_to_gltf(gltf_root, gltf_mat)
        return {}

    # arr = np.loadtxt(pydxhr_matlib, delimiter=",", dtype=int)
    # tex_arr = arr[np.where(arr[:, 0] == cdc_material_id)]

    tx_dict: Dict[int, int] = {}  # key: cdcTX ID, v: gltfTX index
    image_dict: Dict[int, gltf.Image] = {}

    gltf_mat = gltf.Material(
        extras={},
        extensions={},
        name=f"{mat_name}",
        alphaCutoff=0.0,
        alphaMode=gltf.OPAQUE,
        doubleSided=False,
        pbrMetallicRoughness=_empty_pbr(empty_texture_index),
        normalTexture=_empty_normal(empty_texture_index),
        # occlusionTexture=_empty_occlusion(empty_texture_index),
    )

    _modify_emissive(gltf_mat, empty_texture_index)

    if mat_name in mtl_lib:
        mat_info = mtl_lib[mat_name]
    else:
        mat_info = inc_mtl_lib[mat_name]

    for mat_key, tx_id in mat_info.items():
        if mat_key == "unknown" and len(tx_id):
            gltf_mat.extras |= {mat_key: str(tx_id)}
            continue
        if mat_key == "alpha":
            if tx_id == 1:
                gltf_mat.alphaMode = gltf.MASK
                gltf_mat.alphaCutoff = 0.5
            continue
        if mat_key == "light" and len(tx_id):
            gltf_mat.emissiveFactor = [1, 1, 1]

        if len(tx_id) == 0:
            continue

        if len(tx_id) > 1:
            gltf_mat.extras |= {
                mat_key: ",".join(["T_" + f"{t:x}".rjust(8, '0') if isinstance(t, int) else t for t in tx_id])
            }
            if mat_key == "colors":
                # why is this here as opposed to outside the if len(tx_id)?
                # this will "automatically" exclude the "dummyblack" color,
                # so this will only trigger if "flatX" is in the list
                if len(mat_info.get("diffuse")):
                    # this means that there's already something in pbr.basecolor
                    # and we can just ignore what colors are attached
                    continue
                else:
                    colors = [i.strip().replace("flat", "") for i in tx_id if "flat" in i]
                    if len(colors) > 1:
                        # haha idk
                        pass
                    elif len(colors) == 1:
                        match colors[0]:
                            case "black":
                                gltf_mat.pbrMetallicRoughness.baseColorFactor = [0, 0, 0, 1]
                            case "white":
                                gltf_mat.pbrMetallicRoughness.baseColorFactor = [1, 1, 1, 1]
                            case "grey":
                                gltf_mat.pbrMetallicRoughness.baseColorFactor = [0.5, 0.5, 0.5, 1]
                            case "normal":
                                pass
                            case _:
                                pass
                                # breakpoint()
                        continue

            for tx in tx_id:
                if isinstance(tx, int):
                    _ = _add_image(int(tx), ignore_mat_key=True)
            continue

        if len(tx_id) == 1:
            gltf_mat.extras |= {
                mat_key: "T_" + f"{tx_id[0]:x}".rjust(8, '0') if isinstance(tx_id[0], int) else tx_id[0]
            }

            try:
                tx = int(tx_id[0])
            except ValueError:
                pass  # TODO
            except TypeError:
                tx = tx_id[0][0]
            else:
                gltf_tx_id = _add_image(int(tx), ignore_mat_key=True)

                if gltf_tx_id is None:
                    continue

                tf = gltf.TextureInfo(
                    index=gltf_tx_id,
                    texCoord=0,
                    extensions={
                        "KHR_texture_transform": {
                            "offset": [0, 0],
                            "rotation": 0,
                            "scale": [1, 1],
                            "texCoord": 0
                        }
                    }
                )

                match mat_key:
                    case "diffuse":
                        gltf_mat.pbrMetallicRoughness.baseColorTexture = tf
                    case "normal":
                        gltf_mat.normalTexture.index = gltf_tx_id
                    # case "blend":
                    #     pass
                    case "specular":
                        gltf_mat.extensions["KHR_materials_specular"] = {
                            "specularColorTexture": tf,
                            "specularColorFactor": [1, 1, 1]
                        }
                    # case "mask":
                    #     pass
                    # case "colors":
                    #     pass
                    case "light":
                        gltf_mat.emissiveTexture = tf
                    case _:
                        pass

    # elif mat_name in inc_mtl_lib:
    #     gltf_mat = gltf.Material(
    #         name=f"{mat_name}",
    #         extras=inc_mtl_lib[mat_name]
    #     )
    #
    #     for mat_key, tx_id in inc_mtl_lib[mat_name].items():
    #         breakpoint()
        # _add_image(int(tx), ignore_mat_key=True)

    _add_to_gltf(gltf_root, gltf_mat)

    # seen = []
    # materials = {}
    # matlib_data = {}
    # for tex_id, tex_info in zip(tex_arr[:, 1], tex_arr[:, 2:]):
    #     if tex_id in seen:
    #         continue
    #
    #     mat_type = guess_materials(*tex_info)
    #     matlib_data[str(tex_id.item())] = str(tex_info.tolist())
    #
    #     if mat_type not in materials:
    #         materials[mat_type] = []
    #     materials[mat_type].append(tex_id.item())
    #
    #     seen.append(tex_id.item())
    #
    # len_mats = max(len(images) for images in materials.values())
    # materials_fixed = [dict(zip(materials, t)) for t in itertools.zip_longest(*materials.values())]
    # image_list = list(itertools.chain.from_iterable(materials.values()))
    #
    # if blank_materials:
    #     gltf_mat = gltf.Material(
    #         name=f"{mat_name}",
    #         extras=matlib_data
    #     )
    #
    #     for tx_id in matlib_data.keys():
    #         _add_image(int(tx_id), ignore_mat_key=True)
    #
    #     _add_to_gltf(gltf_root, gltf_mat)
    # else:
    #     for i, mat in enumerate(materials_fixed):
    #         gltf_mat = gltf.Material(
    #             name=f"{mat_name}",
    #             extras=mat,
    #         )
    #
    #         if i == 0:
    #             for mat_key, tx_id in mat.items():
    #                 if not tx_id:
    #                     continue
    #
    #                 gltf_tx_id = _add_image(tx_id)
    #
    #                 if gltf_tx_id:
    #                     tf = gltf.TextureInfo(index=gltf_tx_id)
    #
    #                     match mat_key:
    #                         case "diffuse":
    #                             gltf_mat.pbrMetallicRoughness = gltf.PbrMetallicRoughness(baseColorTexture=tf)
    #                         case "normal":
    #                             gltf_mat.normalTexture = gltf.NormalMaterialTexture(index=gltf_tx_id)
    #                         case "blend":
    #                             pass
    #                         case _:
    #                             pass
    #
    #             _add_to_gltf(gltf_root, gltf_mat)
    #         else:  # add dangling images + textures, but not attach to any materials - these can be fixed later,
    #             # depending on the settings of the GLTF importer
    #             for mat_key, tx_id in mat.items():
    #                 if not tx_id:
    #                     continue
    #
    #                 _ = _add_image()

    return image_dict


def _add_index_data(
        array: np.ndarray,
        binary_blob: bytes,
        mesh_num: int = -1,
        submesh_num: int = -1,
        name: str = ""
) -> Tuple[gltf.BufferView, gltf.Accessor, bytes]:
    current_byte_offset = len(binary_blob)

    byte_data = array.flatten().tobytes()
    view = gltf.BufferView(
        buffer=0,
        byteOffset=current_byte_offset,
        byteLength=len(byte_data),
        target=gltf.ELEMENT_ARRAY_BUFFER,
        name=f"Mesh_{mesh_num}_Prim_{submesh_num}_indices",
        extras={
            "MESH_NAME": name,
            "MESH_IDX": mesh_num,
            "PRIM_IDX": submesh_num,
        },
    )

    accessor = gltf.Accessor(
        componentType=gltf.UNSIGNED_INT,
        count=array.size,
        type=gltf.SCALAR,
        max=[int(array.max())],
        min=[int(array.min())],
        name=f"Mesh_{mesh_num}_Prim_{submesh_num}_indices",
        extras={
            "MESH_NAME": name,
            "MESH_IDX": mesh_num,
            "PRIM_IDX": submesh_num,
        },
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
        _PACKEDNTB=attribute_index_dict[VertexSemantic.PackedNTB.value],
    )


def _add_vertex_data(
        vtx_sem: VertexSemantic,
        vtx_array: np.ndarray,
        binary_blob: bytes,
        mesh_num: int = -1,
        name: str = ""
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
        vtx_array = _add_tangent_handedness(vtx_array)

    elif vtx_sem.value in VertexSemantic.colors():
        # I'm not sure if this is correct, but if it gets the GLTF validator to shut up...
        vtx_array = np.abs(vtx_array)

    current_byte_offset = len(binary_blob)
    byte_data = vtx_array.tobytes()

    view = gltf.BufferView(
        buffer=0,
        byteOffset=current_byte_offset,
        byteLength=len(byte_data),
        target=gltf.ARRAY_BUFFER,
        extras={
            "MESH_NAME": name,
            "MESH_IDX": mesh_num,
            "VTX_SEM": VertexSemantic.as_gltf_attr(vtx_sem),
        },
        name=f"Mesh_{mesh_num}_{vtx_sem.name}"
    )

    accessor = gltf.Accessor(
        componentType=gltf.FLOAT,
        count=len(vtx_array),
        # max=[round(i, 2) for i in np.max(v, axis=0).tolist()],
        # min=[round(i, 2) for i in np.min(v, axis=0).tolist()],
        name=f"Mesh_{mesh_num}_{vtx_sem.name}",
        extras={
            "MESH_NAME": name,
            "MESH_IDX": mesh_num,
            "VTX_SEM": VertexSemantic.as_gltf_attr(vtx_sem),
        },
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


def _add_to_gltf(gltf_root: gltf.GLTF2, item: gltf.Property, **extras) -> int:
    """
    Adds a GLTF property to the GLTF object according to its type and returns the index of the property

    :param gltf_root:
    :param item:
    :return:
    """
    item.extras |= extras

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


def _create_buffer(
        gltf_root: gltf.GLTF2,
        binary_blob: bytes,
        name: str
) -> None:
    """
    Generates a buffer for binary blob and attaches it to the GLTF root

    :param gltf_root:
    :param binary_blob:
    :return:
    """

    buffer = gltf.Buffer(
        extras={
            "name": name
        }
    )
    buffer.byteLength = len(binary_blob)
    gltf_root.buffers.append(buffer)

    gltf_root.set_binary_blob(binary_blob)


def _add_tangent_handedness(v: np.ndarray, reverse: bool = False) -> np.ndarray:
    """
    See GLTF spec

    :param v:
    :param reverse:
    :return:
    """
    handedness = 1 if not reverse else -1
    return np.hstack([v, handedness*np.ones((1, v.shape[0])).T])


def _empty_pbr(empty_tex_index: int):
    tf = gltf.TextureInfo(
        index=empty_tex_index,
        texCoord=0,
        extensions={
            "KHR_texture_transform": {
                "offset": [0, 0],
                "rotation": 0,
                "scale": [1, 1],
                "texCoord": 0
            }
        }
    )

    return gltf.PbrMetallicRoughness(
        metallicFactor=0.0,
        roughnessFactor=1.0,
        # baseColorFactor=[0.0, 0.0, 0.0, 1.0],
        baseColorTexture=tf,
        # metallicRoughnessTexture=tf
    )


def _empty_normal(empty_tex_index: int):
    return gltf.NormalMaterialTexture(
        index=empty_tex_index,
        texCoord=0,
        scale=1.0
    )


def _empty_occlusion(empty_tex_index: int):
    return gltf.OcclusionTextureInfo(
        index=empty_tex_index,
        texCoord=0,
        strength=1.0
    )


def _modify_emissive(
        mat: gltf.Material,
        empty_tex_index: Optional[int] = None,
        emissive_factor: Tuple = (0.0, 0.0, 0.0)
):
    mat.emissiveTexture = gltf.TextureInfo(
        index=empty_tex_index,
        texCoord=0,
        extensions={
            "KHR_texture_transform": {
                "offset": [0, 0],
                "rotation": 0,
                "scale": [1, 1],
                "texCoord": 0
            }
        }
    )

    mat.emissiveFactor = list(emissive_factor)
