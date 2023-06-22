from abc import abstractmethod
from pathlib import Path
from typing import Optional

from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.utils.MeshData import MeshData
from pyDXHR.cdcEngine.DRM.Section import Section, SectionSubtype
from pyDXHR.cdcEngine.Sections import AbstractSection


class RenderMesh(AbstractSection):
    def __init__(self, **kwargs):
        self.MeshData = MeshData()
        super().__init__(**kwargs)

    @staticmethod
    @abstractmethod
    def _get_name_from_archive(archive, sec_id):
        raise NotImplementedError

    @abstractmethod
    def _deserialize_from_section(self, section: Section):
        super()._deserialize_from_section(section)
        self._section = section
        self.MeshData.MaterialIDList = self._material_ids

    @property
    @abstractmethod
    def _material_ids(self):
        pass

    def to_gltf(self, **kwargs):
        # dest = None
        save_to = kwargs.get("save_to", None)

        if save_to:
            if Path(save_to).is_dir():
                kwargs["save_to"] = Path(save_to) / Path(self.Name).stem
            # else:
            #     dest = save_to

        return self.MeshData.as_gltf(
            name=Path(self.Name).stem,
            # save_to=dest,
            **kwargs
        )

    def to_obj(self, **kwargs):
        return self.MeshData.as_obj(**kwargs)


def deserialize(section: Section):
    from pyDXHR.cdcEngine.Sections.RenderModel import RenderModel
    from pyDXHR.cdcEngine.Sections.RenderTerrain import RenderTerrain

    out = None
    match section.Header.SectionSubtype:
        case SectionSubtype.RenderModel:
            out = RenderModel(section=section)
        case SectionSubtype.RenderTerrain:
            out = RenderTerrain(section=section)
        case _:
            pass

    return out


def deserialize_drm(drm: DRM):
    return {deserialize(sec) for sec in drm.Sections if deserialize(sec)}
