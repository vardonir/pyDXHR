from copy import copy
from typing import Dict
import numpy as np
from pyDXHR.utils.MeshData import VertexSemantic, read_vertex_buffer
from pyDXHR.utils import Endian

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
    def from_file(cls, filename):
        with open(filename, 'rb') as f:
            byte_data = f.read()

        obj = super().from_file(filename)
        obj.byte_data = byte_data
        return obj

    @property
    def Header(self):
        return self.data.header

    @property
    def Indices(self) -> np.ndarray:
        return np.array(self.data.indices, dtype=np.uint32).reshape((-1, 3))

    @property
    def Vertices(self) -> Dict[int, Dict[VertexSemantic, np.ndarray]]:
        assert len(self.data.vtx_buffer) == len(self.data.vtx_sem_info)

        for vb, vs in zip(self.data.vtx_buffer, self.data.vtx_sem_info):
            vtx_data = self.byte_data[vb.off_vtx_buffer:]

            for sem in vs.semantics:
                out = read_vertex_buffer(
                    vertex_data=vtx_data,
                    semantic_type=sem.type,
                    semantic_offset=sem.offset,
                    count=vb.len_vtx_buffer,
                    stride=vs.len_vtx,
                    endian=self.Endian)

            breakpoint()

        return {}

    @property
    def Materials(self):
        pass

if __name__ == "__main__":
    pc_sample_file = r"F:\Projects\pyDXHR\playground\rt_pc.bin"
    ps3_sammple_file = r"F:\Projects\pyDXHR\playground\rt_ps3.bin"

    krt_pc = KaitaiRenderTerrain.from_file(pc_sample_file)

    krt_pc.Vertices
    breakpoint()
