"""
Handles all RenderMesh related sections - overloads the kaitai-generated classes and then parses it as MeshData
"""

from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import numpy as np
from pyDXHR.DRM import DRM, Section
from pyDXHR.generated.render_model_buffer import (
    RenderModelBuffer as KaitaiRenderModelBuffer,
)

from pyDXHR.export.mesh import MeshData
from pyDXHR.generated.render_terrain import RenderTerrain as KaitaiRenderTerrain
from pyDXHR import VertexAttribute


class RenderMesh(ABC):
    """RenderMesh section types"""

    def __init__(self):
        self.byte_data = b""
        self.endian: str = "<"
        self.materials = []
        self.section_id: int = 0
        self.file_name: Optional[str] = None

    def read(self):
        """Read the mesh data"""
        return self.parse_mesh_data()

    @abstractmethod
    def parse_mesh_data(self) -> MeshData:
        """Abstract method. Parse mesh data."""
        raise NotImplementedError


class RenderModel(RenderMesh):
    """
    PC: Splits the RenderModel section between the header and the mesh data, which is marked by the "Mesh" bytes.
    Consoles: The RenderModel section contains just the header.

    Procedure:
    Find the part where the "Mesh" bytes are located, and split the section into two parts.
    The first part is some kind of header that I don't really care much about.
    The second part is the same data as the RenderModelBuffer section for the consoles, which
    contains the actual indices, vertices, etc.
    If the section doesn't contain the "Mesh" bytes, then it's a console version of the section, which
    means that there is no mesh data in this section.
    """

    def __init__(self, section: Section):
        super().__init__()
        self.section = section
        self.file_name = self.section.header.file_name
        self.section_id = section.header.section_id
        section_data = self.section.data

        buffer_mark_le = section_data.find(b"Mesh")
        buffer_mark_be = section_data.find(b"hseM")
        if buffer_mark_le != -1:
            buffer_mark = buffer_mark_le
        elif buffer_mark_be != -1:
            buffer_mark = buffer_mark_be
        else:
            buffer_mark = -1
            self.rmb = None
            # raise ValueError("Mesh data not found")

        if buffer_mark != -1:
            self.rmb: Optional[RenderModelBuffer] = RenderModelBuffer.from_bytes(
                section_data[buffer_mark:]
            )
            self.rmb.materials = _get_materials(section, 0x8)
            self.rmb.byte_data = section_data[buffer_mark:]
            self.rmb.endian = section.header.endian
            self.rmb.section_id = section.header.section_id
        else:
            self.materials = _get_materials(section, 0x8)

        self.rm_data = section_data[:buffer_mark]
        # TODO: I believe there's some information here about bones, but I'm not interested in that right now.

    @classmethod
    def from_section(cls, sec: Section):
        return cls(sec)

    def read(self):
        return self.parse_mesh_data()

    def parse_mesh_data(self):
        """
        Technically speaking, RM sections don't have mesh data, at least in the way that's defined
        here. In particular, the mesh data of the RM section in the PC version is treated as an RMB.
        """
        raise NotImplementedError

    def __repr__(self):
        if self.file_name:
            return f"<{self.__class__.__name__} {self.file_name}>"
        else:
            return f"<{self.__class__.__name__} {self.section_id:08X}>"


class RenderTerrain(KaitaiRenderTerrain, RenderMesh):
    """
    RenderTerrain section - found in both PC and consoles, these are typically large meshes that contain more than
    10 materials. For example, the helipad + ground + background in the Sarif Industries HQ is one big RT.
    """

    def parse_mesh_data(self) -> MeshData:
        """
        Read the RT data using the kaitai parser
        """
        import struct
        from pyDXHR.export.mesh import MeshData

        vertex_buffers = {}
        mesh_prim_indexed = {}

        index_buffer = self.data.indices
        header = self.data.header

        # offset layout / vtx_buffer_info
        # vtx_info_data = self.byte_data[header.offset_vtx_buffer_info:]
        vtx_info = self.data.vtx_sem_info

        # offset vb
        vb_data = self.byte_data[header.offset_vb :]
        for vb, (off_vtx_buffer, unk1, len_vtx_buffer, i_fmt) in enumerate(
            [struct.unpack_from(f"{self.endian}4L", vb_data, 0x10 * i) for i in range(header.len_vb)]
        ):
            vtx_buffer_info = vtx_info[i_fmt]
            vtx_sem_dict = {}
            for vtx_sem in vtx_buffer_info.semantics:
                # normal2 doesn't seem to work in this specific case
                vtx_data = _read_vertex_buffer(
                    vertex_data=self.byte_data[off_vtx_buffer:],
                    semantic_type=vtx_sem.type,
                    semantic_offset=vtx_sem.offset,
                    count=len_vtx_buffer,
                    stride=vtx_buffer_info.len_vtx,
                    endian=self.endian,
                )
                vtx_sem_dict[VertexAttribute(vtx_sem.sem.value)] = vtx_data

            vertex_buffers[vb] = vtx_sem_dict

        index_dict = {}
        # TODO: clean up
        for i in range(header.len_nodes):
            (off_list,) = struct.unpack_from(
                f"{self.endian}L", self.byte_data, header.offset_geom + i * 4
            )
            if off_list == 0 or off_list >= len(self.byte_data) - 2:
                continue
            (n_ranges,) = struct.unpack_from(
                f"{self.endian}H", self.byte_data, off_list
            )

            for j in range(n_ranges):  # range = prim?
                off_range = off_list + 4 + 16 * j
                target, count, start_index = struct.unpack_from(
                    f"{self.endian}HHL", self.byte_data, off_range
                )

                idx_mat, idx_buffer = struct.unpack_from(
                    f"{self.endian}LL",
                    self.byte_data,
                    header.offset_group + target * 0x20,
                )
                assert idx_buffer in range(header.len_vb)
                assert idx_mat in range(header.len_group)

                if idx_buffer not in index_dict:
                    index_dict[idx_buffer] = []

                np_indices = np.array(
                    index_buffer[start_index : start_index + count], dtype=np.uint32
                ).reshape((-1, 3))
                index_dict[idx_buffer].append((idx_mat, np_indices))

        for idx_buffer, items in index_dict.items():
            for idx_mat, vtx in items:
                if idx_buffer not in mesh_prim_indexed:
                    mesh_prim_indexed[idx_buffer] = []

                mesh_prim_indexed[idx_buffer].append((self.materials[idx_mat], vtx))

        # offset group ???
        # offset nodes ???
        # offset something ???
        # offset geom ???

        return MeshData(
            vertex_buffers=vertex_buffers,
            mesh_prim_indexed=mesh_prim_indexed,
            material_list=self.materials,
        )


class RenderModelBuffer(KaitaiRenderModelBuffer, RenderMesh):
    """
    RenderModelBuffer section - it's a separate section in the console versions of the game, but it's
    merged with the RenderModel section in the PC version. This is the data that starts from the "Mesh" header.
    """

    def parse_mesh_data(self) -> MeshData:
        """
        Read the RMB data using the kaitai parser
        """
        from pyDXHR.export.mesh import MeshData

        vertex_buffers = {}
        mesh_prim = {}
        mesh_prim_indexed = {}

        index_buffer = self.header.indices
        mesh_prim_list = self.header.mesh_prim_table
        mesh_headers = self.header.mesh_table
        bbox_sphere_radius = self.header.header.bbox_sphere_radius

        for mp in mesh_prim_list:
            ib_width = mp.len_triangles * 3

            indices = index_buffer[mp.start_index : ib_width + mp.start_index]
            mesh_prim[mp] = np.array(indices, dtype=np.uint32).reshape(
                (mp.len_triangles, 3)
            )

        for mesh_num, mesh in enumerate(mesh_headers):
            if mesh.min_dist > 0.0:
                continue

            vtx_sem_info = mesh.vtx_sem_info
            i_stride, len_attr = vtx_sem_info.len_vtx, vtx_sem_info.len_vtx_sem
            vtx_buffer_data = self.byte_data[mesh.offset_to_vtx_buffer :]

            vtx_sem_dict: Dict[VertexAttribute, np.ndarray] = {}
            for i, vtx in enumerate(vtx_sem_info.semantics):
                vtx_buffer = _read_vertex_buffer(
                    vertex_data=vtx_buffer_data,
                    semantic_type=vtx.type,
                    semantic_offset=vtx.offset,
                    count=mesh.len_vertices,
                    stride=i_stride,
                    endian=self.endian,
                )

                vtx_sem_dict[VertexAttribute(vtx.sem)] = vtx_buffer

            vertex_buffers[mesh_num] = vtx_sem_dict

        grouped = []
        for idx, p in enumerate(mesh_prim_list):
            for m in mesh_headers:
                if m.start_index_buffer == p.start_index:
                    grouped.append(mesh_prim_list[idx : idx + m.len_mesh_parts])

        for grp_num, mesh_prim_list in enumerate(grouped):
            for mp in mesh_prim_list:
                if grp_num not in mesh_prim_indexed:
                    mesh_prim_indexed[grp_num] = []

                mesh_prim_indexed[grp_num].append(
                    (self.materials[mp.ptr_material], mesh_prim[mp])
                )

        return MeshData(
            vertex_buffers=vertex_buffers,
            mesh_prim_indexed=mesh_prim_indexed,
            material_list=self.materials,
            bbox_sphere_radius=bbox_sphere_radius,
        )


def from_section(sec: Section) -> Optional[RenderMesh]:
    """
    Reads a section, identifies the section type and subtype,
    and then reads it according to the appropriate class.

    Outside the from_drm method below, this function is intended
    for use for the internal RM/RT data found in unit DRMs.
    """
    from pyDXHR import SectionType, SectionSubtype

    if sec.header.section_type != SectionType.render_mesh:
        return None

    if sec.header.section_subtype == SectionSubtype.render_model:
        rm = RenderModel.from_section(sec)
        rm.byte_data = sec.data
        rm.endian = sec.header.endian
        rm.file_name = sec.header.file_name
        if rm.rmb is not None:
            return rm.rmb
        else:
            return None
    elif sec.header.section_subtype == SectionSubtype.render_model_buffer:
        rmb = RenderModelBuffer.from_bytes(sec.data)

        rmb.file_name = sec.header.file_name
        rmb.section_id = sec.header.section_id
        rmb.byte_data = sec.data
        rmb.endian = sec.header.endian
        rmb.materials = _get_materials(sec, 0x8)
        return rmb
    elif sec.header.section_subtype == SectionSubtype.render_terrain:
        start_offset = 0
        for res in sec.resolvers:
            if res.pointer_offset == 0x4:
                start_offset = res.data_offset
        mesh_data = sec.data[start_offset:]

        rt = RenderTerrain.from_bytes(mesh_data)
        rt.file_name = sec.header.file_name
        rt.section_id = sec.header.section_id
        rt.endian = sec.header.endian
        rt.byte_data = mesh_data
        rt.materials = _get_materials(sec, 0xC)
        return rt
    else:
        return None


def from_section_pair(rm_sec: Section, rm_buffer_sec: Section) -> Optional[RenderMesh]:
    rm = RenderModel.from_section(rm_sec)
    rmb = from_section(rm_buffer_sec)
    rmb.materials = rm.materials
    rmb.file_name = rm_sec.header.file_name

    return rmb


def from_drm(drm: DRM) -> List[RenderMesh]:
    """
    Convert a DRM to a list of RenderMesh instances
    """
    from pyDXHR import SectionType, SectionSubtype

    if drm.endian == ">":
        rm_list = []
        for i in range(0, len(drm.sections) - 1):
            curr_sec = drm.sections[i]
            next_sec = drm.sections[i + 1]

            if curr_sec.header.section_type == SectionType.render_mesh and next_sec.header.section_type == SectionType.render_mesh:
                if curr_sec.header.section_subtype == SectionSubtype.render_model and next_sec.header.section_subtype == SectionSubtype.render_model_buffer:
                    sec_pair = from_section_pair(curr_sec, next_sec)
                    if sec_pair:
                        rm_list.append(sec_pair)
                        continue

            if curr_sec.header.section_type == SectionType.render_mesh and curr_sec.header.section_subtype == SectionSubtype.render_terrain:
                rm_list.append(from_section(curr_sec))
                continue

        return rm_list

    else:
        return [
            from_section(sec)
            for sec in drm.sections
            if sec.header.section_type == SectionType.render_mesh
        ]


def _get_materials(sec: Section, offset: int = 0) -> List[int]:
    """
    Get the material IDs from the section's resolvers.
    For the RenderModel, the value is taken from https://github.com/rrika/dxhr/blob/main/tools/cdcmesh.py#L771
    And for RenderTerrain, the value is taken from https://github.com/rrika/dxhr/blob/main/tools/cdcmesh.py#L779
    """
    import struct

    mat_ids = []
    for res in sec.resolvers:
        if res.pointer_offset == offset:
            mat_offset = res.data_offset

            if mat_offset:
                endian = sec.header.endian
                (count,) = struct.unpack_from(f"{endian}L", sec.data, mat_offset)

                mat_ids = [
                    struct.unpack_from(f"{endian}L", sec.data, mat_offset + 4 + 4 * i)[
                        0
                    ]
                    for i in range(count)
                ]

    return mat_ids


class UnknownVertexAttribute(Exception):
    pass


def _read_vertex_buffer(
    vertex_data: bytes,
    semantic_type: int,
    semantic_offset: int,
    count: int,
    stride: int,
    endian: str = "<",
) -> np.ndarray:
    """
    From the vertex data, read and convert the data to a numpy array.

    Notes on the types follow.

    match semantic_type:
        0x01                2x float32      probably unused in HR?        used in texcoords for TR
        0x02                3x float32                                    position, normal
        0x04           (same as 0x06?)
        0x05           (same as 0x06?)                                    also normal apparently??
        0x06                4x  uint8       divide by 255      (or 3x?)   blendweights
        0x07                4x  uint8                          (or 3x?)   blendindices
        0x08                    ???                                       packedNTB for rendermodel? found in ps3 version    # noqa
        0x13                 2x sint16      divide by 2048.0              texcoords
        0xA                     ???                                       packedNTB - shows up in RenderTerrain
        0x11                    ???                                       wii-u version. related to Normal/Binormal/Tangent?  # noqa

    :param vertex_data: mesh data starting from the vtx buffer offset
    :param semantic_type: see table above
    :param semantic_offset: offset
    :param count: number of vertices
    :param stride: don't ask me -v
    :param endian: endianness of the input data
    :return: ndarray of vertices, with the correct shape
    """
    import struct

    match semantic_type:
        case 0x02:
            vtx = [
                struct.unpack_from(
                    f"{endian}fff", vertex_data, (i * stride) + semantic_offset
                )
                for i in range(count)
            ]
            return np.array(vtx, dtype=np.float32)
        case 0x04 | 0x05 | 0x06 | 0x8 | 0xA | 0x11:
            # not sure if 0x8 or 0xA belongs here, but it works?
            # 0x11 seems to work but the output looks weird
            vtx = [
                struct.unpack_from(
                    f"{endian}BBB", vertex_data, (i * stride) + semantic_offset
                )
                for i in range(count)
            ]
            out_array = np.array(vtx, dtype=np.float32)
            out_array = out_array / 255 * 2 - 1
            out_array = out_array / np.linalg.norm(out_array, axis=1)[:, None]
            return out_array
        case 0x07:
            vtx = [
                struct.unpack_from(
                    f"{endian}BBB", vertex_data, (i * stride) + semantic_offset
                )
                for i in range(count)
            ]
            return np.array(vtx, dtype=np.float32)
        case 0x13:
            vtx = [
                struct.unpack_from(
                    f"{endian}hh", vertex_data, (i * stride) + semantic_offset
                )
                for i in range(count)
            ]
            return np.array(vtx, dtype=np.float32) / 2048
        case _:
            raise UnknownVertexAttribute(f"Found: {semantic_type}")
