from io import BytesIO
import struct
from pathlib import Path
from enum import Enum
import numpy as np

from typing import Dict, Tuple, Optional, List
from pyDXHR.KaitaiGenerated.RenderModel import RenderModel
from pyDXHR.KaitaiGenerated.RenderTerrainHeader import RenderTerrainHeader
from pyDXHR.KaitaiGenerated.RenderTerrainGroup import RenderTerrainGroup
from pyDXHR.KaitaiGenerated.Vertices import VertexInfo
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionSubtype
from pyDXHR.utils import Endian


class KaitaiRenderModel(RenderModel):
    @property
    def Header(self):
        return self.header.header

    @property
    def IndexBuffer(self):
        return self.header.indices

    @property
    def MeshTable(self):
        return self.header.mesh_table

    @property
    def MeshPrimitiveTable(self):
        return self.header.mesh_prim_table


class VertexSemantic(Enum):
    Position = 0xd2f7d823
    Normal = 0x36f5e414
    Normal2 = 0x3E7F6149  # i'm guessing that the real name is not "Normal2", but I needed to name it something
    TesselationNormal = 0x097879bd
    Tangent = 0xf1ed11c3
    Binormal = 0x64a86f01
    PackedNTB = 0x09b1d4ea
    SkinWeights = 0x48e691c0
    SkinIndices = 0x5156d8d3
    Color1 = 0x7e7dd623
    Color2 = 0x733ef0fa
    TexCoord1 = 0x8317902a
    TexCoord2 = 0x8e54b6f3
    TexCoord3 = 0x8a95ab44
    TexCoord4 = 0x94d2fb41

    @staticmethod
    def tex_coords() -> set:
        return {VertexSemantic.TexCoord1.value, VertexSemantic.TexCoord2.value,
                VertexSemantic.TexCoord3.value, VertexSemantic.TexCoord4.value}

    @staticmethod
    def colors() -> set:
        return {VertexSemantic.Color1.value, VertexSemantic.Color2.value}

    @staticmethod
    def tangents() -> set:
        return {VertexSemantic.Tangent.value, VertexSemantic.Binormal.value}

    @staticmethod
    def normals() -> set:
        return {VertexSemantic.Normal.value, VertexSemantic.Normal2.value}


class MeshData:
    def __init__(self):
        self._endian: Endian = Endian.Little
        self._subtype: Optional[SectionSubtype] = None
        self._mat_id_list: Optional[List[int]] = None
        self._trs_matrix: Optional[np.ndarray] = None

        self._rm_mesh_headers = []
        self._rm_mesh_prim_list = []
        self._rm_mesh_prim_indices = {}

        self._rt_index_dict: Dict[int, List[Tuple[int, np.ndarray]]] = {}

        self.VertexBuffers: Dict[int, Dict[VertexSemantic, np.ndarray]] = {}

    @property
    def MaterialIDList(self):
        from pyDXHR.cdcEngine.Sections.Material import Material

        mlist = []
        for mid in self._mat_id_list:
            mat = Material()
            mat.ID = mid
            mlist.append(mat)
        return mlist

    @MaterialIDList.setter
    def MaterialIDList(self, mat_id_list: List[int]):
        self._mat_id_list = mat_id_list

    # noinspection PyPep8Naming
    @property
    def MeshPrimIndexed(self):
        from pyDXHR.cdcEngine.Sections.Material import Material

        match self._subtype:
            case SectionSubtype.RenderModel | SectionSubtype.RenderModelBuffer:
                grouped = []
                for idx, p in enumerate(self._rm_mesh_prim_list):
                    for m in self._rm_mesh_headers:
                        if m.start_index_buffer == p.start_index:
                            grouped.append(self._rm_mesh_prim_list[idx:idx+m.len_mesh_parts])

                out = {}
                for grp_num, mesh_prim_list in enumerate(grouped):
                    for mp in mesh_prim_list:
                        mat = Material()
                        if self._mat_id_list:
                            mat.ID = self._mat_id_list[mp.ptr_material]
                        if grp_num not in out:
                            out[grp_num] = []

                        out[grp_num].append((mat, self._rm_mesh_prim_indices[mp]))

                return out
            case SectionSubtype.RenderTerrain:
                cleaned = {}
                for idx_buffer, items in self._rt_index_dict.items():
                    for idx_mat, vtx in items:
                        if idx_buffer not in cleaned:
                            cleaned[idx_buffer] = []

                        cleaned[idx_buffer].append((self.MaterialIDList[idx_mat], vtx))

                return cleaned
            case _:
                raise NotImplementedError

    def deserialize(self, data, data_type, endian: Endian = Endian.Little):
        self._endian = endian

        match data_type.__qualname__:
            case "RenderModel":
                self._subtype = SectionSubtype.RenderModel
                self._from_RenderModel(data)
            case "RenderTerrain":
                self._subtype = SectionSubtype.RenderTerrain
                self._from_RenderTerrain(data)
            case "RenderModelBuffer":
                self._subtype = SectionSubtype.RenderModelBuffer
                self._from_RenderModel(data)
            case _:
                raise KeyError

    # noinspection PyPep8Naming
    def _from_RenderTerrain(self, mesh_data):
        # adapted from https://github.com/rrika/cdcEngineDXHR/blob/main/rendering/TerrainData.h
        header = RenderTerrainHeader.from_io(BytesIO(mesh_data))

        # offset indices
        index_buffer = struct.unpack_from(f"{self._endian.value}{header.len_indices}H", mesh_data, header.offset_indices)

        # offset layout
        vtx_info_data_buffer = BytesIO(mesh_data[header.offset_layout:])
        vtx_info = [VertexInfo.from_io(vtx_info_data_buffer) for i in range(header.len_layout)]

        # offset vb
        vb_data_buffer = BytesIO(mesh_data[header.offset_vb:])
        for vb in range(header.len_vb):
            off_vtx_buffer, unk1, len_vtx_buffer, i_fmt = struct.unpack_from(
                f"{self._endian.value}LLLL", vb_data_buffer.read(0x10))

            vtx_buffer_info = vtx_info[i_fmt]
            vtx_sem_dict = {}
            for vtx_sem in vtx_buffer_info.vtxsem:
                # TODO: normal2 doesnt seem to work + need to figure out packedntb
                vtx_data = read_vertex_buffer(vertex_data=mesh_data[off_vtx_buffer:],
                                              semantic_type=vtx_sem.type,
                                              semantic_offset=vtx_sem.offset,
                                              count=len_vtx_buffer,
                                              stride=vtx_buffer_info.len_vtx,
                                              endian=self._endian
                                              )
                vtx_sem_dict[VertexSemantic(vtx_sem.sem)] = vtx_data

            self.VertexBuffers[vb] = vtx_sem_dict

        # offset group (target)
        group_data_buffer = BytesIO(mesh_data[header.offset_group:])
        groups = [RenderTerrainGroup.from_io(group_data_buffer) for i in range(header.len_group)]
        # number of unique material indices in the groups list seems to correlate
        # with number of material indices of RT. might be related?

        # offset node (lists)
        node_data_buffer = BytesIO(mesh_data[header.offset_node:])

        # TODO: wtf is going on here
        for i in range(header.len_nodes):
            off_list, = struct.unpack_from(f"{self._endian.value}L", mesh_data, header.offset_geom + i*4)
            if off_list == 0 or off_list >= len(mesh_data) - 2:
                continue
            n_ranges, = struct.unpack_from(f"{self._endian.value}H", mesh_data, off_list)

            for j in range(n_ranges):
                off_range = off_list + 4 + 16*j
                target, count, start_index = struct.unpack_from(f"{self._endian.value}HHL", mesh_data, off_range)

                idx_mat, idx_buffer = struct.unpack_from(f"{self._endian.value}LL", mesh_data, header.offset_group + target * 0x20)
                assert idx_buffer in range(header.len_vb)
                assert idx_mat in range(header.len_group)

                if idx_buffer not in self._rt_index_dict:
                    self._rt_index_dict[idx_buffer] = []

                np_indices = np.array(index_buffer[start_index:start_index+count], dtype=np.uint32).reshape((-1, 3))
                self._rt_index_dict[idx_buffer].append((idx_mat, np_indices))

        # probably material-related?
        # for g in groups:
        #     if g.idx_vb == idx_buffer and g.idx_material == idx_mat :
        #         test[g] = (self.VertexBuffers[idx_buffer], index_buffer[start_index:start_index+count])
        #     if g in test:
        #         found_test = test[g]
        #         if index_buffer[start_index:start_index+count] == found_test[1]:
        #             continue
        #         else:
        #             breakpoint()

        # offset geom something is missing here
        # geom_data_buffer = BytesIO(mesh_data[header.offset_geom:])

        # offset dword3c something (not used)
        # not implemented

    # noinspection PyPep8Naming
    def _from_RenderModel(self, data):
        # TODO: insert *dramatic Shatner voice* here: BONES!

        ksy = KaitaiRenderModel.from_bytes(data)
        index_buffer = ksy.IndexBuffer

        self._rm_mesh_prim_list = ksy.MeshPrimitiveTable
        for mp in self._rm_mesh_prim_list:
            ib_width = mp.len_triangles * 3

            indices = index_buffer[mp.start_index:ib_width + mp.start_index]
            self._rm_mesh_prim_indices[mp] = np.array(indices, dtype=np.uint32).reshape((mp.len_triangles, 3))

        self._rm_mesh_headers = ksy.MeshTable
        for mesh_num, mesh in enumerate(self._rm_mesh_headers):
            if mesh.min_dist > 0.0:
                continue

            vtx_sem_info = mesh.vtx_sem_info
            i_stride, len_attr = vtx_sem_info.len_vtx, vtx_sem_info.len_vtx_sem
            vtx_buffer_data = data[mesh.offset_to_vtx_buffer:]

            vtx_sem_dict: Dict[VertexSemantic, np.ndarray] = {}
            for i, vtx in enumerate(vtx_sem_info.semantics):
                vtx_buffer = read_vertex_buffer(
                    vertex_data=vtx_buffer_data,
                    semantic_type=vtx.type,
                    semantic_offset=vtx.offset,
                    count=mesh.len_vertices,
                    stride=i_stride,
                    endian=self._endian)

                vtx_sem_dict[VertexSemantic(vtx.sem)] = vtx_buffer

            self.VertexBuffers[mesh_num] = vtx_sem_dict

    def as_gltf(self,
                name: Optional[str],
                save_to: Optional[str | Path] = None,
                as_bytes: bool = False,
                apply_scale: bool = False,
                blank_materials: bool = False):
        from pyDXHR.utils.gltf import build_gltf
        return build_gltf(
            mesh_data=self,
            as_bytes=as_bytes,
            name=name,
            save_to=save_to,
            apply_scale=apply_scale,
            blank_materials=blank_materials
        )


def read_vertex_buffer(vertex_data: bytes,
                       semantic_type: int,
                       semantic_offset: int,
                       count: int,
                       stride: int,
                       endian: Endian = Endian.Little) -> np.ndarray:
    """
    match semantic_type:
        0x01                2x float32      probably unused in HR?        used in texcoords for TR
        0x02                3x float32                                    position, normal
        0x04           (same as 0x06?)
        0x05           (same as 0x06?)                                    also normal apparently??
        0x06                4x  uint8       divide by 255      (or 3x?)   blendweights
        0x07                4x  uint8                          (or 3x?)   blendindices
        0x13                 2x sint16      divide by 2048.0              texcoords
        0xA     3x float32 + 2x uint16                                    packedNTB - shows up in RenderTerrain

    :param vertex_data: mesh data starting from the vtx buffer offset
    :param semantic_type: see table above
    :param semantic_offset:
    :param count: number of vertices
    :param stride:
    :param endian: endianess of the input data
    :return: ndarray of vertices
    """

    match semantic_type:
        case 0x01:
            raise NotImplementedError
        case 0x02:
            vtx = [struct.unpack_from(f"{endian.value}fff", vertex_data, (i * stride) + semantic_offset) for i in range(count)]
            return np.array(vtx, dtype=np.float32)
        case 0x04 | 0x05 | 0x06 | 0xA:
            # not sure if 0xA belongs here, but it works?
            vtx = [struct.unpack_from(f"{endian.value}BBB", vertex_data, (i * stride) + semantic_offset) for i in range(count)]
            out_array = np.array(vtx, dtype=np.float32)
            out_array = out_array / 255 * 2 - 1
            out_array = out_array / np.linalg.norm(out_array, axis=1)[:, None]
            return out_array
        case 0x07:
            vtx = [struct.unpack_from(f"{endian.value}BBB", vertex_data, (i * stride) + semantic_offset) for i in range(count)]
            return np.array(vtx, dtype=np.float32)
        case 0x13:
            vtx = [struct.unpack_from(f"{endian.value}hh", vertex_data, (i * stride) + semantic_offset) for i in range(count)]
            return np.array(vtx, dtype=np.float32) / 2048
        case _:
            raise Exception(f"Unknown vertex semantic type: {semantic_type}")
