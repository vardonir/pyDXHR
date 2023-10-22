from typing import List, Optional
from pathlib import Path
from pyDXHR.DRM import DRM, Section
from pyDXHR.export.dds import Image
from pyDXHR import SectionType, SectionSubtype
from pyDXHR.generated.pcd import Pcd as KaitaiPCD9
from pyDXHR.generated.ps3t import Ps3t as KaitaiPS3T
from kaitaistruct import KaitaiStructError


class RenderResource:
    def __init__(self):
        self.byte_data: bytes = b""
        self.section_id: int = -1
        self.resource_name: Optional[str] = None
        self.file_name: Optional[str] = None

        self.unk14: int = -1
        self.unk18: int = -1

    def read(self):
        return self.parse_resource_data()

    def parse_resource_data(self):
        raise NotImplementedError

    def __repr__(self):
        if self.file_name:
            return f"<{self.__class__.__name__} {self.file_name}>"
        else:
            return f"<{self.__class__.__name__} {self.section_id:08X}>"


class Texture(RenderResource):
    def parse_resource_data(self):
        parsed = None
        try:
            parsed = KaitaiPCD9.from_bytes(self.byte_data)
        except KaitaiStructError:
            pass
        else:
            self.unk14 = parsed.unk14
            self.unk18 = parsed.unk18

        try:
            parsed = KaitaiPS3T.from_bytes(self.byte_data)
            self.resource_name = Path(self.file_name).stem.replace("|", "_")
        except KaitaiStructError:
            pass

        if parsed is None:
            raise NotImplementedError("Could not parse texture data (yet)")

        return Image(
            width=parsed.width,
            height=parsed.height,
            tex_fmt_str=parsed.format.name,
            payload=parsed.payload,
            name=self.resource_name
            if self.resource_name is not None
            else f"{self.section_id:08x}"
            # len_mipmaps=parsed.len_mipmaps
        )

    @classmethod
    def from_bytes(cls, data: bytes):
        obj = cls()
        obj.byte_data = data
        return obj


def from_section(section: Section) -> Optional[RenderResource]:
    if section.header.section_type == SectionType.render_resource:
        if section.header.section_subtype == SectionSubtype.texture:
            tex = Texture.from_bytes(section.data)
            tex.section_id = section.header.section_id
            tex.file_name = section.header.file_name
            return tex


def from_drm(drm: DRM) -> List[RenderResource]:
    return [
        from_section(sec)
        for sec in drm.sections
        if sec.header.section_type == SectionType.render_resource
    ]
