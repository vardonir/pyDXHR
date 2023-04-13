import warnings
from typing import Optional

from pyDXHR.cdcEngine.Sections.RenderMesh import RenderMesh
from pyDXHR.cdcEngine.DRM.Section import Section
from pyDXHR.cdcEngine.Archive import ArchivePlatform


class RenderModelBuffer(RenderMesh):
    def __init__(self, rm_sec: Optional[Section] = None, **kwargs):
        self._render_model_section = rm_sec
        super().__init__(**kwargs)

    @property
    def RenderModelSection(self):
        return self._render_model_section

    @RenderModelSection.setter
    def RenderModelSection(self, sec):
        self._render_model_section = sec

    @staticmethod
    def _get_name_from_archive(archive, m_id):
        if archive is not None and archive.platform.value in ArchivePlatform.has_complete_file_lists():
            return archive.section_list[m_id]
        else:
            return "RenderModelBuffer_" + f"{m_id:x}".rjust(8, '0')

    def _deserialize_from_section(self, sec: Section):
        if self._render_model_section is None:
            warnings.warn("RMSec not attached, materials will not be processed")
        super()._deserialize_from_section(sec)
        self.MeshData.deserialize(sec.Data, data_type=RenderModelBuffer)

    @property
    def _material_ids(self):
        from pyDXHR.cdcEngine.Sections.Material import get_material_ids
        if self._render_model_section:
            return get_material_ids(self._render_model_section, 0x8)
        else:
            warnings.warn("RMSec not attached, materials will not be processed")
