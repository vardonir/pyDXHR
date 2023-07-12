from typing import Dict, Tuple, List
import numpy as np
from pyDXHR.utils.MeshData import VertexSemantic, read_vertex_buffer
from pyDXHR.utils import Endian
import struct
from io import BytesIO

from pyDXHR.cdcEngine.Sections.RenderMesh import RenderMesh
from pyDXHR.cdcEngine.DRM.Resolver import find_resolver
from pyDXHR.cdcEngine.DRM.Section import Section
from pyDXHR.cdcEngine.Archive import ArchivePlatform
from pyDXHR.KaitaiGenerated.RenderTerrain import RenderTerrain as KRT


class RenderTerrain(RenderMesh):
    @staticmethod
    def _get_name_from_archive(archive, m_id):
        if archive is not None and archive.platform.value in ArchivePlatform.has_complete_file_lists():
            return archive.section_list[m_id]
        else:
            return "RenderTerrain_" + f"{m_id:x}".rjust(8, '0')

    def _deserialize_from_section(self, section: Section):
        super()._deserialize_from_section(section)

        res = find_resolver(section.Resolvers, offset=0x4)
        mesh_data = section.Data[res.DataOffset:]

        self.MeshData.deserialize(mesh_data, data_type=RenderTerrain, endian=section.Header.Endian)

    @property
    def _material_ids(self):
        from pyDXHR.cdcEngine.Sections.Material import get_material_ids
        return get_material_ids(self._section, 0xC)


class KaitaiRenderTerrain(KRT):
    def __init__(self, _io, _parent=None, _root=None):
        super().__init__(_io, _parent, _root)
        self.byte_data: bytes = b""
        self.Endian: Endian = Endian.Little

    @classmethod
    def from_bytes(cls, buf):
        obj = super().from_bytes(buf)
        obj.Endian = Endian.Little if obj.flags < 65535 else Endian.Big
        obj.byte_data = buf
        return obj

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'rb') as f:
            byte_data = f.read()

        obj = super().from_file(filename)
        obj.Endian = Endian.Little if obj.flags < 65535 else Endian.Big
        obj.byte_data = byte_data
        return obj

    @property
    def Header(self):
        return self.data.header

    @property
    def Indices(self) -> np.ndarray:
        out = np.array(self.data.indices, dtype=np.uint32).reshape((-1, 3))
        assert not np.any(np.isnan(out))
        return out

    @property
    def Vertices(self) -> Dict[int, Dict[VertexSemantic, np.ndarray]]:
        assert len(self.data.vtx_buffer) == len(self.data.vtx_sem_info)

        vertex_buffers = {}
        vb_data_buffer = BytesIO(self.byte_data[self.data.header.offset_vb:])
        for idx, vb in enumerate(self.data.vtx_buffer):
            off_vtx_buffer, unk1, len_vtx_buffer, i_fmt = struct.unpack_from(
                f"{self.Endian.value}LLLL", vb_data_buffer.read(0x10))

            vtx_sem_dict = {}
            vtx_buffer_info = self.data.vtx_sem_info[i_fmt]
            for sem in vtx_buffer_info.semantics:
                out = read_vertex_buffer(
                    vertex_data=self.byte_data[off_vtx_buffer:],
                    semantic_type=sem.type,
                    semantic_offset=sem.offset,
                    count=len_vtx_buffer,
                    stride=vtx_buffer_info.len_vtx,
                    endian=self.Endian)

                assert not np.any(np.isnan(out))
                vtx_sem_dict[VertexSemantic(sem.sem.value)] = out

            vertex_buffers[idx] = vtx_sem_dict

        return vertex_buffers

    @property
    def Materials(self) -> Dict[int, List[Tuple[int, np.ndarray]]]:
        # TODO no seriously wtf, fix this plz
        # seems like a mixup in the terminology/variable names...
        mat_idx_dict = {}
        for i in range(self.data.header.len_nodes):
            off_list, = struct.unpack_from(f"{self.Endian.value}L", self.byte_data, self.data.header.offset_geom + i*4)
            if off_list == 0 or off_list >= len(self.byte_data) - 2:
                continue
            n_ranges, = struct.unpack_from(f"{self.Endian.value}H", self.byte_data, off_list)

            for j in range(n_ranges):  # range = prim?
                off_range = off_list + 4 + 16*j
                target, count, start_index = struct.unpack_from(f"{self.Endian.value}HHL", self.byte_data, off_range)

                idx_mat, idx_buffer = struct.unpack_from(f"{self.Endian.value}LL", self.byte_data,
                                                         self.data.header.offset_group + target * 0x20)
                assert idx_buffer in range(self.data.header.len_vb)
                assert idx_mat in range(self.data.header.len_group)

                if idx_buffer not in mat_idx_dict:
                    mat_idx_dict[idx_buffer] = []

                mat_idx_dict[idx_buffer].append((idx_mat, self.Indices))

        return mat_idx_dict


if __name__ == "__main__":
    pc_sample_file = r"F:\Projects\pyDXHR\playground\rt_pc.bin"
    ps3_sammple_file = r"F:\Projects\pyDXHR\playground\rt_ps3.bin"

    krt_pc = KaitaiRenderTerrain.from_file(pc_sample_file)
    breakpoint()
