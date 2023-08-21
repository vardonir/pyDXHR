"""
A unified class for compiling the vertex data in the render mesh sections
so that it can be exported to GLTF.
"""
from pathlib import Path
from typing import List, Optional, Tuple
import warnings
import numpy as np
import pygltflib as gl

from pyDXHR import VertexAttribute
from pyDXHR.DRM.Section import Material
import os
from dotenv import load_dotenv
load_dotenv()


class MeshData:
    """ Compiles the vertex data along with the material data to export to GLTF """
    def set_material_data(self, materials: List[int]):
        self.materials = materials

    @staticmethod
    def generate_asset_metadata():
        asset_data = gl.Asset()
        asset_data.generator = "pyDXHR"
        asset_data.version = "2.0"
        asset_data.copyright = "2011 (c) Eidos Montreal"
        return asset_data

    def _populate_constants(self):
        """ Add the constants to the GLTF file - metadata and the empty texture"""
        import base64

        self.gltf_root.asset = self.generate_asset_metadata()
        self.gltf_root.extras = {
            "MeshDataName": self.name
        }

        empty_image = gl.Image(
            name="empty",
            mimeType="image/png",
        )

        index_empty_image = self._add_property(empty_image)
        empty_texture = gl.Texture(
            source=index_empty_image,
            name="empty",
        )
        _ = self._add_property(empty_texture)

        image = generate_black_image()
        encoded = base64.b64encode(image)

        empty_image_buffer = gl.Buffer(
            uri='data:application/octet-stream;base64,{}'.format(str(encoded).split("'")[1]),
            byteLength=len(image)
        )

        empty_image_buffer_view = gl.BufferView(
            name="empty",
            buffer=1,
            byteLength=empty_image_buffer.byteLength
        )
        index_empty_image_buffer_view = self._add_property(empty_image_buffer_view)
        empty_image.bufferView = index_empty_image_buffer_view

        self.gltf_root.buffers.append(empty_image_buffer)

    def __init__(self,
                 vertex_buffers,
                 mesh_prim_indexed,
                 material_list,
                 name: Optional[str] = None,
                 bbox_sphere_radius: int = -1
                 ):

        self._skip_textures = bool(os.getenv("skip_textures", True))
        self._is_built = False

        self.bbox_sphere_radius = bbox_sphere_radius
        self.vertex_buffers = vertex_buffers
        self.mesh_prim_indexed = mesh_prim_indexed
        self.material_list = material_list
        self.name: str = name
        self.materials: Optional[List[int]] = None

        self.trs_matrix = None
        self.gltf_root = gl.GLTF2()
        self._binary_blob = b''
        
        self._parent_node = gl.Node(
            name=self.name
        )
        self._parent_node.extras = {
            "bbox_sphere_radius": bbox_sphere_radius
        }
        index_parent_node = self._add_property(self._parent_node)

        scene_node = gl.Scene()
        scene_node.nodes = [index_parent_node]
        index_scene = self._add_property(scene_node)
        self.gltf_root.scene = index_scene

        self._gltf_mesh_prim_list = []

    def build_gltf(self):
        # add the materials

        material_index_dict = {}
        if self._skip_textures:
            for mat in self.material_list:
                gltf_mat = gl.Material(
                    name=f"M_{mat:08X}",
                    extras={},
                    alphaCutoff=None
                )

                index_mat = self._add_property(gltf_mat)
                material_index_dict[mat] = index_mat
        else:
            raise NotImplementedError

        # add vertex/index data

        for idx, (_, vtx_sem_dict) in enumerate(self.vertex_buffers.items()):
            attribute_index_dict = {k.value: None for k in VertexAttribute}

            for vtx_sem, array in vtx_sem_dict.items():
                vtx_buffer_view, vtx_accessor, vtx_byte_data = self._add_vertex_data(
                    vtx_sem=vtx_sem,
                    vtx_array=array,
                    binary_blob=self._binary_blob,
                    mesh_num=idx,
                    name=self.name,
                )

                self._binary_blob += vtx_byte_data
                vtx_buffer_view_index = self._add_property(vtx_buffer_view)
                vtx_accessor.bufferView = vtx_buffer_view_index
                attribute_index_dict[vtx_sem.value] = vtx_buffer_view_index

                _ = self._add_property(vtx_accessor)

            mesh_attributes = self._populate_mesh_attributes(attribute_index_dict)

            mesh_prim_list: List[Tuple[int, np.ndarray]] = self.mesh_prim_indexed[idx]

            for imp, (mat, arr) in enumerate(mesh_prim_list):
                accessor_index = len(self.gltf_root.accessors)

                idx_buffer_view, idx_accessor, idx_byte_data = self._add_index_data(array=arr,
                                                                                    binary_blob=self._binary_blob,
                                                                                    mesh_num=idx, sub_mesh_num=imp,
                                                                                    name=self.name)

                self._binary_blob += idx_byte_data
                idx_buffer_view_index = self._add_property(idx_buffer_view)
                idx_accessor.bufferView = idx_buffer_view_index
                _ = self._add_property(idx_accessor)

                mesh_prim = gl.Primitive(
                    attributes=mesh_attributes,
                    indices=accessor_index,
                    material=material_index_dict.get(mat),
                    extras={
                        "MESH_NAME": self.name,
                        "MESH_IDX": idx,
                        "PRIM_IDX": imp,
                        "cdcMatID": f"{mat:08X}",
                    }
                )

                self._gltf_mesh_prim_list.append(mesh_prim)

        self._is_built = True

    def to_lumen_gltf(self, save_to: Optional[str | Path] = None):
        """ UE5/Lumen GLTF """
        if not self._is_built:
            self.build_gltf()

        mtl_list = []
        for idx, prim in enumerate(self._gltf_mesh_prim_list):
            mesh = gl.Mesh(
                name=f"SM_{self.name}_{idx}",
            )
            mesh.primitives = [prim]
            node = gl.Node(
                name=f"N_{self.name}_{idx}",
                mesh=self._add_property(mesh),
            )

            self._parent_node.children.append(self._add_property(node))
        return self._finalize(save_to=save_to)

    def to_gltf(self, save_to: Optional[str | Path] = None):
        """ As-is from the game GLTF """
        if not self._is_built:
            self.build_gltf()

        mesh = gl.Mesh(
            name=self.name
        )
        mesh_index = self._add_property(mesh)
        self._parent_node.mesh = mesh_index

        mesh.primitives = self._gltf_mesh_prim_list
        return self._finalize(save_to=save_to)

    def _finalize(self, save_to: Optional[str | Path] = None):

        buffer = gl.Buffer(
            extras={
                "name": self.name
            }
        )
        buffer.byteLength = len(self._binary_blob)
        self.gltf_root.buffers.append(buffer)

        self.gltf_root.set_binary_blob(self._binary_blob)

        self._populate_constants()
        apply_global_node_transform(self._parent_node)

        if save_to:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=UserWarning)
                self.gltf_root.save(save_to)

        else:
            return self.gltf_root

    def _add_property(self, item: gl.Property, **extras) -> int:
        """
        Adds a GLTF property to the GLTF object according to its type and returns the index of the property
        """
        item.extras |= extras

        li: List[gl.Property]
        match type(item).__qualname__:
            case gl.Node.__qualname__:
                li = self.gltf_root.nodes
            case gl.Mesh.__qualname__:
                li = self.gltf_root.meshes
            case gl.Material.__qualname__:
                li = self.gltf_root.materials
            case gl.Accessor.__qualname__:
                li = self.gltf_root.accessors
            case gl.BufferView.__qualname__:
                li = self.gltf_root.bufferViews
            case gl.Image.__qualname__:
                li = self.gltf_root.images
            case gl.Scene.__qualname__:
                li = self.gltf_root.scenes
            case gl.Texture.__qualname__:
                li = self.gltf_root.textures
            case _:
                raise KeyError

        index = len(li)
        li.append(item)
        return index

    @staticmethod
    def _add_index_data(
            array: np.ndarray,
            binary_blob: bytes,
            mesh_num: int = -1,
            sub_mesh_num: int = -1,
            name: str = ""
    ) -> Tuple[gl.BufferView, gl.Accessor, bytes]:
        current_byte_offset = len(binary_blob)

        byte_data = array.flatten().tobytes()
        view = gl.BufferView(
            buffer=0,
            byteOffset=current_byte_offset,
            byteLength=len(byte_data),
            target=gl.ELEMENT_ARRAY_BUFFER,
            name=f"Mesh_{mesh_num}_Prim_{sub_mesh_num}_indices",
            extras={
                "MESH_NAME": name,
                "MESH_IDX": mesh_num,
                "PRIM_IDX": sub_mesh_num,
            },
        )

        accessor = gl.Accessor(
            componentType=gl.UNSIGNED_INT,
            count=array.size,
            type=gl.SCALAR,
            max=[np.max(array).item()],
            min=[np.min(array).item()],
            name=f"Mesh_{mesh_num}_Prim_{sub_mesh_num}_indices",
            extras={
                "MESH_NAME": name,
                "MESH_IDX": mesh_num,
                "PRIM_IDX": sub_mesh_num,
            },
        )

        return view, accessor, byte_data

    def _add_vertex_data(self,
                         vtx_sem: VertexAttribute,
                         vtx_array: np.ndarray,
                         binary_blob: bytes,
                         mesh_num: int = -1,
                         name: str = ""
                         ) -> Tuple[gl.BufferView, gl.Accessor, bytes]:
        """
        Transforms a vertex semantic/vertex numpy array to a GLTF buffer view + Accessor + byte data

        :param vtx_sem:
        :param vtx_array:
        :param binary_blob:
        :param mesh_num:
        :return:
        """
        if vtx_sem.value in {VertexAttribute.tangent.value, VertexAttribute.binormal.value}:
            vtx_array = self._add_tangent_handedness(vtx_array)

        elif vtx_sem.value in {VertexAttribute.color1.value, VertexAttribute.color2.value}:
            # I'm not sure if this is correct, but if it gets the GLTF validator to shut up...
            vtx_array = np.abs(vtx_array)

        current_byte_offset = len(binary_blob)
        byte_data = vtx_array.tobytes()

        view = gl.BufferView(
            buffer=0,
            byteOffset=current_byte_offset,
            byteLength=len(byte_data),
            target=gl.ARRAY_BUFFER,
            extras={
                "MESH_NAME": name,
                "MESH_IDX": mesh_num,
                "VTX_SEM": vtx_attr_as_gltf_attr(vtx_sem),
            },
            name=f"Mesh_{mesh_num}_{vtx_sem.name}"
        )

        accessor = gl.Accessor(
            componentType=gl.FLOAT,
            count=len(vtx_array),
            # max=[round(i, 2) for i in np.max(v, axis=0).tolist()],
            # min=[round(i, 2) for i in np.min(v, axis=0).tolist()],
            name=f"Mesh_{mesh_num}_{vtx_sem.name}",
            extras={
                "MESH_NAME": name,
                "MESH_IDX": mesh_num,
                "VTX_SEM": vtx_attr_as_gltf_attr(vtx_sem),
            },
        )

        if vtx_sem.value in {VertexAttribute.texcoord1.value, VertexAttribute.texcoord2.value}:
            accessor.type = gl.VEC2
        elif vtx_sem.value in {VertexAttribute.tangent.value, VertexAttribute.binormal.value}:
            accessor.type = gl.VEC4
        elif vtx_sem.value in {VertexAttribute.normal.value, VertexAttribute.normal2.value}:
            accessor.type = gl.VEC3
        elif vtx_sem.value is VertexAttribute.position.value:
            accessor.type = gl.VEC3
            accessor.min = [round(min(vtx_array[:, i])) - 1 for i in range(3)]
            accessor.max = [round(max(vtx_array[:, i])) - 1 for i in range(3)]
        else:
            accessor.type = gl.VEC3

        return view, accessor, byte_data

    @staticmethod
    def _add_tangent_handedness(v: np.ndarray, reverse: bool = False) -> np.ndarray:
        handedness = 1 if not reverse else -1
        return np.hstack([v, handedness*np.ones((1, v.shape[0])).T])

    @staticmethod
    def _populate_mesh_attributes(attribute_index_dict: dict) -> gl.Attributes:
        """
        Transforms a dictionary of attribute indices to the GLTF Attribute object

        :param attribute_index_dict:
        :return:
        """
        return gl.Attributes(
            POSITION=attribute_index_dict[VertexAttribute.position.value],
            NORMAL=attribute_index_dict[VertexAttribute.normal.value],
            TANGENT=attribute_index_dict[VertexAttribute.tangent.value],

            TEXCOORD_0=attribute_index_dict[VertexAttribute.texcoord1.value],
            TEXCOORD_1=attribute_index_dict[VertexAttribute.texcoord2.value],

            COLOR_0=attribute_index_dict[VertexAttribute.color1.value],
            COLOR_1=attribute_index_dict[VertexAttribute.color2.value],

            # TODO: not implemented
            JOINTS_0=None,
            WEIGHTS_0=None,

            # included in file for archival purposes
            _BINORMAL=attribute_index_dict[VertexAttribute.binormal.value],
            _NORMAL2=attribute_index_dict[VertexAttribute.normal2.value],  # so confused
            _PACKEDNTB=attribute_index_dict[VertexAttribute.packed_ntb.value],
        )


def generate_black_image():
    """ Generates a black image """
    from PIL import Image
    import io

    image = np.zeros((4, 4, 4), dtype=np.uint8)
    image[..., 3] = 255

    image = Image.fromarray(image)

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


def vtx_attr_as_gltf_attr(vtx_sem) -> str:
    if vtx_sem.value in {VertexAttribute.position.value, VertexAttribute.normal.value, VertexAttribute.tangent.value}:
        return vtx_sem.name.upper()
    elif vtx_sem.value in {VertexAttribute.texcoord1, VertexAttribute.texcoord2}:
        return ("".join([i for i in vtx_sem.name][:-1])).upper() + f"_{int([i for i in vtx_sem.name][-1]) - 1}"
    elif vtx_sem.value in {VertexAttribute.color1, VertexAttribute.color2}:
        return ("".join([i for i in vtx_sem.name][:-1])).upper() + f"_{int([i for i in vtx_sem.name][-1]) - 1}"
    else:
        # GLTF spec says that unused attributes should have a leading underscore
        return "_" + vtx_sem.name.upper()


def apply_node_transformations(node: gl.Node, **kwargs):
    """ Apply a transformation to a node and return the same node """
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


def apply_global_node_transform(node: gl.Node):
    from scipy.spatial.transform import Rotation

    uniform_scale = float(os.getenv("model_scale", 1))
    use_z_up = bool(os.getenv("model_z_up", False))

    return apply_node_transformations(
        node,
        scale=3 * [uniform_scale],
        rotation=Rotation.from_euler('x', -90, degrees=True).as_quat().tolist() if use_z_up else None
    )