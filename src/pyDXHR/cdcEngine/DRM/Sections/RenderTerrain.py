from cdcEngine.DRM.Sections.RenderMesh import RenderMesh
from pyDXHR.cdcEngine.DRM.Resolver import find_resolver
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionSubtype
from pyDXHR.cdcEngine.DRM.Section import Section
from pyDXHR.cdcEngine.Archive import ArchivePlatform


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
        from cdcEngine.DRM.Sections.Material import get_material_ids
        return get_material_ids(self._section, 0xC)
