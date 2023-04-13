from pathlib import Path
from typing import Optional

from pyDXHR.cdcEngine.Sections.RenderMesh import RenderMesh
from pyDXHR.cdcEngine.DRM.Section import Section


class CollisionMesh(RenderMesh):
    @staticmethod
    def _get_name_from_archive(archive, sec_id):
        pass

    def _deserialize_from_section(self, section: Section):
        pass

    @property
    def _material_ids(self):
        return -1
