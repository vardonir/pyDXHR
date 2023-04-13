import warnings

from pyDXHR.cdcEngine.Archive import ArchivePlatform
from pyDXHR.cdcEngine.Sections.RenderMesh import RenderMesh
from pyDXHR.cdcEngine.DRM.Section import Section

from pyDXHR.utils import Endian


class RenderModel(RenderMesh):
    @staticmethod
    def _get_name_from_archive(archive, m_id):
        if archive is not None and archive.platform.value in ArchivePlatform.has_complete_file_lists():
            return archive.section_list[m_id]
        else:
            return "RenderModel_" + f"{m_id:x}".rjust(8, '0')

    @staticmethod
    def _magic(endian: Endian = Endian.Little):
        return b"Mesh" if endian == Endian.Little else b'Mesh'[::-1]

    def _deserialize_from_section(self, sec: Section):
        super()._deserialize_from_section(sec)

        mesh_data_start = sec.Data.find(self._magic(self._endian))
        if mesh_data_start == -1:
            warnings.warn("RenderModel needs RMBuffer - only getting material data")
        else:
            mesh_data = sec.Data[mesh_data_start:]

            self.MeshData.deserialize(mesh_data, data_type=RenderModel, endian=sec.Header.Endian)

    @property
    def _material_ids(self):
        from pyDXHR.cdcEngine.Sections.Material import get_material_ids
        return get_material_ids(self._section, 0x8)
