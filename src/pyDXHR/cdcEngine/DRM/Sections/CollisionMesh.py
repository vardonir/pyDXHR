from pathlib import Path
from typing import Optional

from pyDXHR.cdcEngine.DRM.Sections import RenderMesh
from pyDXHR.cdcEngine.DRM.Section import Section


class CollisionMesh(RenderMesh):
    # TODO
    def deserialize(self, inp):
        pass

    def _deserialize_section(self, section: Section):
        pass

    @property
    def _material_ids(self):
        return -1

    def as_gltf(self,
                name: Optional[str] = None,
                save_to: Optional[str | Path] = None):
        name = f"CollisionMesh_0x{self._section.Header.IdHexString}" if name is None else name
        super().as_gltf(name=name, save_to=save_to)
