""" WIP script to make working with GLTFs involve less counting """

import pygltflib as gl
import networkx as nx
from typing import *
from pygltflib.validator import summary
import numpy as np
from PIL import Image
import warnings
from dataclasses_json import dataclass_json as dataclass_json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass_json
@dataclass
class NamedPrimitive(gl.Primitive):
    name: Optional[str] = None
    __qualname__ = "pygltfnet.NamedPrimitive"


gl.Primitive = NamedPrimitive


class AccessBuffer:
    __qualname__ = "pygltfnet.AccessBuffer"
    __slots__ = (
        "name",
        "Accessor",
        "AttributeType",
        "BufferView",
        "RawData",
    )

    name: str
    Accessor: gl.Accessor
    AttributeType: str
    BufferView: gl.BufferView
    RawData: bytes

    def __init__(self,
                 data: np.ndarray,
                 attribute_type: str,
                 name: str,
                 override_accessor_type: Optional[str] = None) -> None:
        self.name = name
        self.AttributeType = attribute_type.upper()
        self.RawData = data.flatten().tobytes()  # if self.AttributeType == "INDEX" else data.tobytes()

        accessor_type = override_accessor_type if override_accessor_type else self._accessor_type(self.AttributeType)
        component_type = gl.UNSIGNED_INT if self.AttributeType == "INDEX" else gl.FLOAT
        min_value = [int(data.min())] if self.AttributeType == "INDEX" else [round(i, 2) for i in
                                                                             np.min(data, axis=0).tolist()]
        max_value = [int(data.max())] if self.AttributeType == "INDEX" else [round(i, 2) for i in
                                                                             np.max(data, axis=0).tolist()]
        count = data.size if self.AttributeType == "INDEX" else len(data)
        bv_target = gl.ELEMENT_ARRAY_BUFFER if self.AttributeType == "INDEX" else gl.ARRAY_BUFFER

        self.Accessor: gl.Accessor = gl.Accessor(
            name=name,
            count=count,
            componentType=component_type,
            type=accessor_type,
            max=max_value,
            min=min_value,
        )

        self.BufferView: gl.BufferView = gl.BufferView(
            name=name,
            byteLength=len(self.RawData),
            buffer=0,
            target=bv_target,
        )

    def __repr__(self) -> str:
        return self.BufferView.__repr__() + self.Accessor.__repr__()

    def _accessor_type(self, attribute_type: str):
        if attribute_type in {"POSITION"}:
            return gl.VEC3
        if attribute_type == "INDEX":
            return gl.SCALAR
        if attribute_type == "TANGENT":
            return gl.VEC3
        if "TEXCOORD" in attribute_type:
            return gl.VEC2


@dataclass
class TextureDefinition:
    __qualname__ = "pygltfnet.TextureDefinition"
    Diffuse: Optional[Image.Image | str | Path] = None
    MetallicRoughness: Optional[Image.Image | str | Path] = None
    Normal: Optional[Image.Image | str | Path] = None
    Occulsion: Optional[Image.Image | str | Path] = None
    Emissive: Optional[Image.Image | str | Path] = None
    name: str = ""


class GLTFDiGraph:
    def __init__(self, **kwargs):
        self._digraph: nx.DiGraph = nx.DiGraph()
        self._root_node = self._digraph.add_node("ROOT")
        self._root_scene: Optional[gl.Scene] = None

        self._options_split_buffers = kwargs.get("split_buffers", False)
        self._options_embed_images = kwargs.get("embed_images", False)

    def save(self, **kwargs):
        save_to_path = kwargs.get("save_to", None)
        save_textures_path = kwargs.get("save_textures_to", None)
        as_bytes = kwargs.get("as_bytes", False)
        blank_materials = kwargs.get("blank_materials", False)

        gltf_root = gl.GLTF2()
        byte_data = b""

        for n in self._digraph.nodes:
            gltf_prop = self._digraph.nodes[n].get("property")
            if gltf_prop:
                if isinstance(gltf_prop, AccessBuffer):
                    acc_list = self._get_property_list_from_gltf(gltf_root, gl.Accessor)
                    bv_list = self._get_property_list_from_gltf(gltf_root, gl.BufferView)

                    acc = gltf_prop.Accessor
                    bv = gltf_prop.BufferView

                    bv.byteOffset = len(byte_data)
                    # acc.byteOffset = len(byte_data)
                    acc.bufferView = len(bv_list)

                    acc_list.append(acc)
                    bv_list.append(bv)

                    byte_data += gltf_prop.RawData
                else:
                    prop_list = self._get_property_list_from_gltf(gltf_root, type(gltf_prop))
                    if prop_list is not None:
                        prop_list.append(gltf_prop)

        # post-processing
        # connect set root scene
        gltf_root.scene = self._get_root_scene_index(gltf_root, self._root_scene)

        for_linking = (
            (gl.Scene, gl.Node),
            (gl.Node, gl.Node),
            (gl.Node, gl.Mesh),
        )

        # connect gltf properties
        for f, t in for_linking:
            links = self._get_linked_properties(f, t)
            # fl = self._get_property_list_from_gltf(gltf_root, f)
            tl = self._get_property_list_from_gltf(gltf_root, t)
            if tl:
                for li in links:
                    self._create_link(tl.index(li[1]), li[0], li[1])

        # connect mesh - primitive
        # primitives are not added to the gltf root, only attached to a mesh
        mesh_prim = self._get_linked_properties(gl.Mesh, NamedPrimitive)
        for m, p in mesh_prim:
            p.name = None  # gltf validator throws a fit with it
            m.primitives.append(p)

        # connect primitive - indices (accessor/buffer view)
        prim_indices_access = self._get_linked_properties(NamedPrimitive, AccessBuffer)
        acc_list = self._get_property_list_from_gltf(gltf_root, gl.Accessor)
        for p, ab in prim_indices_access:
            match ab.AttributeType:
                case "INDEX":
                    p.indices = acc_list.index(ab.Accessor)
                case "POSITION":
                    p.attributes.POSITION = acc_list.index(ab.Accessor)

        # connect primitive - material
        mat_prim = self._get_linked_properties(gl.Material, NamedPrimitive)
        mat_list = self._get_property_list_from_gltf(gltf_root, gl.Material)
        for mat, p in mat_prim:
            p.material = mat_list.index(mat)

        # connect textures - material
        mat_tex = self._get_linked_properties(gl.Material, TextureDefinition)
        for mat, td in mat_tex:
            self._generate_images(gltf_root, mat, td)

        # create buffer
        buffer = gl.Buffer()
        buffer.byteLength = len(byte_data)
        gltf_root.buffers.append(buffer)

        gltf_root.set_binary_blob(byte_data)

        if save_to_path:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=UserWarning)
                gltf_root.save(save_to_path)

        gltf_root.save_json("test.json")
        summary(gltf_root)

    def save_graph(self, **kwargs):
        raise NotImplementedError
        # import matplotlib.pyplot as plt
        #
        # # nx.nx_agraph.graphviz_layout(self._digraph, prog="dot")
        # nx.draw(self._digraph, with_labels=kwargs.get("with_labels", True))
        # plt.savefig(kwargs.get("save_fig", "fig.png"))

    @staticmethod
    def _generate_images(gltf_root: gl.GLTF2, material: gl.Material, texture_definition: TextureDefinition):
        mat_indices = {}
        for k, v in asdict(texture_definition).items():
            if k == "name":
                continue
            if v is None:
                continue

            if isinstance(v, Image.Image):
                raise NotImplementedError
            else:
                image_index = len(gltf_root.images)

                mat_indices[k] = image_index
                im = gl.Image(
                    uri=v,
                    name=Path(v).stem
                )

                gltf_root.images.append(im)

        diffuse = None
        if "Diffuse" in mat_indices:
            diffuse = gl.TextureInfo(
                index=mat_indices["Diffuse"]
            )

        metal_roughness = None
        if "MetallicRoughness" in mat_indices:
            metal_roughness = gl.TextureInfo(
                index=mat_indices["MetallicRoughness"]
            )

        pbr = gl.PbrMetallicRoughness(
            baseColorTexture=diffuse,
            metallicRoughnessTexture=metal_roughness
        )

        normal = None
        if "Normal" in mat_indices:
            normal = gl.NormalMaterialTexture(
                index=mat_indices["Normal"]
            )

        occlusion = None
        if "Occulsion" in mat_indices:
            occlusion = gl.OcclusionTextureInfo(
                index=mat_indices["Occulsion"]
            )

        emissive = None
        if "Emissive" in mat_indices:
            emissive = gl.TextureInfo(
                index=mat_indices["Emissive"]
            )

        material.pbrMetallicRoughness = pbr
        material.normalTexture = normal
        material.occlusionTexture = occlusion
        material.emissiveTexture = emissive

    @staticmethod
    def _create_link(index: int, *args):
        if len(args) != 2:
            raise Exception
        match (type(args[0]), type(args[1])):
            case (gl.Scene, gl.Node):
                args[0].nodes.append(index)
            case (gl.Node, gl.Node):
                args[0].children.append(index)
            case (gl.Node, gl.Mesh):
                args[0].mesh = index
            case _:
                raise Exception(str(args))

    @staticmethod
    def _get_property_list_from_gltf(gltf_root, prop: type):
        match prop:
            case gl.Scene:
                return gltf_root.scenes
            case gl.Node:
                return gltf_root.nodes
            case gl.Mesh:
                return gltf_root.meshes
            case gl.BufferView:
                return gltf_root.bufferViews
            case gl.Accessor:
                return gltf_root.accessors
            case gl.Material:
                return gltf_root.materials
            case gl.Image:
                return gltf_root.images
            case _:
                return None

    def _get_linked_properties(self, *args):
        if len(args) != 2:
            raise Exception

        node_pairs = []
        for f, t, y in self._digraph.edges(data=True):
            if y.get("node_type_from") == args[0].__qualname__ and y.get("node_type_to") == args[1].__qualname__:
                nf = self._digraph.nodes[self._digraph.edges[f, t]['node_from']].get("property")
                nt = self._digraph.nodes[self._digraph.edges[f, t]['node_to']].get("property")
                if nf and nt:
                    node_pairs.append((nf, nt))
        return node_pairs

    @staticmethod
    def _get_root_scene_index(gltf_root, scene):
        root_scene = [i for i, s in enumerate(gltf_root.scenes) if s.name == scene.name]
        if len(root_scene) == 1:
            return root_scene[0]
        else:
            return 0

    @staticmethod
    def _build_graph_name(prop: gl.Property):
        # generates a name that the digraph will use for the added property
        if prop.name is None:
            raise NameError
        return f"{type(prop).__qualname__}_{prop.name}"

    def _add_node_to_graph(self, *args):
        for prop in args:
            self._digraph.add_node(
                self._build_graph_name(prop),
                property=prop,
                property_type=type(prop).__qualname__
            )

    def _add_edge(self, *args):
        for props in args:
            if len(props) != 2:
                raise Exception
            else:
                self._digraph.add_edge(
                    self._build_graph_name(props[0]),
                    self._build_graph_name(props[1]),
                    node_from=self._build_graph_name(props[0]),
                    node_to=self._build_graph_name(props[1]),
                    node_type_from=type(props[0]).__qualname__,
                    node_type_to=type(props[1]).__qualname__,
                )

    def _get_nodes_of_type(self, prop_type: type) -> List[gl.Property]:
        return [y['property']
                for x, y in self._digraph.nodes(data=True)
                if y.get("property_type") == prop_type.__qualname__]

    def add_scene(self, scene: gl.Scene):
        self._add_node_to_graph(scene)
        self._digraph.add_edge("ROOT", self._build_graph_name(scene), node_from="ROOT", node_to=gl.Scene.__qualname__)

    def add_node(self, node: gl.Node):
        self._add_node_to_graph(node)

    def add_mesh(self, mesh: gl.Mesh):
        self._add_node_to_graph(mesh)

    def add_primitive(self, primitive: gl.Primitive):
        self._add_node_to_graph(primitive)

    def add_material(self, material: gl.Material):
        self._add_node_to_graph(material)

    def link_node_to_scene(self, scene: gl.Scene, node: gl.Node):
        self._add_edge((scene, node))

    def link_primitive_to_mesh(self, primitive: gl.Primitive, mesh: gl.Mesh):
        self._add_edge((mesh, primitive))

    def link_node_and_node(self, node1: gl.Node, node2: gl.Node):
        self._add_edge((node1, node2))

    def link_mesh_and_node(self, mesh: gl.Mesh, node: gl.Node):
        self._add_edge((node, mesh))

    def link_material_to_primitive(self, material: gl.Material, primitive: gl.Primitive):
        self._add_edge((material, primitive))

    # link custom properties
    def link_access_buffer_to_property(self, access_buffer: AccessBuffer, prop: gl.Mesh | gl.Primitive):
        acc_buffer_name = f"AB_{access_buffer.name}"
        self._digraph.add_node(
            acc_buffer_name,
            property=access_buffer,
            property_type=AccessBuffer.__qualname__
        )
        self._digraph.add_edge(
            self._build_graph_name(prop),
            acc_buffer_name,
            node_from=self._build_graph_name(prop),
            node_to=acc_buffer_name,
            node_type_from=type(prop).__qualname__,
            node_type_to=AccessBuffer.__qualname__,
        )

    def link_texture_definition_to_material(self, texture_def: TextureDefinition, material: gl.Material):
        tex_def_name = f"TEX_{material.name}"
        self._digraph.add_node(
            tex_def_name,
            property=texture_def,
            property_type=TextureDefinition.__qualname__
        )
        self._digraph.add_edge(
            self._build_graph_name(material),
            tex_def_name,
            node_from=self._build_graph_name(material),
            node_to=tex_def_name,
            node_type_from=type(material).__qualname__,
            node_type_to=TextureDefinition.__qualname__,
        )

    # setters
    def set_default_scene(self, scene: gl.Scene):
        if not scene.name:
            raise NameError
        self._root_scene = scene

    @staticmethod
    def set_node_transformation(node: gl.Node, **kwargs):
        trs_mat = kwargs.get("matrix", None)
        rot = kwargs.get("rotation", None)
        scl = kwargs.get("scale", None)
        loc = kwargs.get("translation", None)

        if trs_mat:
            if isinstance(trs_mat, np.ndarray):
                node.matrix = trs_mat.flatten().tolist()
                return
            elif isinstance(trs_mat, list):
                node.matrix = trs_mat
                return
            else:
                raise TypeError

        node.translation = loc
        node.rotation = rot
        node.scale = scl



# points = np.array(
#     [
#         [-0.5, -0.5, 0.5],
#         [0.5, -0.5, 0.5],
#         [-0.5, 0.5, 0.5],
#         [0.5, 0.5, 0.5],
#         [0.5, -0.5, -0.5],
#         [-0.5, -0.5, -0.5],
#         [0.5, 0.5, -0.5],
#         [-0.5, 0.5, -0.5],
#     ],
#     dtype="float32",
# )
# triangles = np.array(
#     [
#         [0, 1, 2],
#         [3, 2, 1],
#         [1, 0, 4],
#         [5, 4, 0],
#         [3, 1, 6],
#         [4, 6, 1],
#         [2, 3, 7],
#         [6, 7, 3],
#         [0, 2, 5],
#         [7, 5, 2],
#         [5, 7, 4],
#         [6, 4, 7],
#     ],
#     dtype="int",
# )
#
# g = GLTFDiGraph()
# sc1 = gl.Scene(name="1")
# sc2 = gl.Scene(name="2")
# no1, no2, no3 = gl.Node(name="n1"), gl.Node(name="n2"), gl.Node(name="n3")
# mesh1 = gl.Mesh(name="1")
# mp1, mp2 = gl.Primitive(name="1"), gl.Primitive(name="2")
# mat1 = gl.Material(name="mat1")
#
# g.add_material(mat1)
#
# g.add_scene(sc1)
# g.add_scene(sc2)
# g.add_node(no1)
# g.add_node(no2)
# g.link_node_to_scene(sc1, no1)
# g.link_node_to_scene(sc1, no2)
# g.link_node_to_scene(sc2, no1)
#
# g.set_default_scene(sc1)
#
# g.add_mesh(mesh1)
# g.add_primitive(mp1)
# g.add_primitive(mp2)
#
# g.link_primitive_to_mesh(mp1, mesh1)
# g.link_primitive_to_mesh(mp2, mesh1)
#
# g.link_mesh_and_node(mesh1, no1)
# g.link_mesh_and_node(mesh1, no2)
#
# pt_accbuff = AccessBuffer(triangles, "INDEX", "index")
# tris_accbuff = AccessBuffer(points, "POSITION", "position")
#
# g.link_access_buffer_to_property(pt_accbuff, mp1)
# g.link_access_buffer_to_property(tris_accbuff, mp1)
#
# g.link_access_buffer_to_property(pt_accbuff, mp2)
# g.link_access_buffer_to_property(tris_accbuff, mp2)
#
# g.link_material_to_primitive(mat1, mp1)
#
# g.set_node_transformation(no2, scale=[1, 2, 3])
#
# # tex = Image.open("uv_checker.jpg")
# tex_def = TextureDefinition(
#     Diffuse="uv_checker.jpg"
# )
#
# g.link_texture_definition_to_material(tex_def, mat1)
#
# g.save_graph()
# g.save(save_to="test.gltf")
