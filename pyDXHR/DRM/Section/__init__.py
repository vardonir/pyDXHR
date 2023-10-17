"""
For reading the section data.
"""

import struct
from typing import List, Optional

from pyDXHR import SectionType, SectionSubtype
from pyDXHR.generated.dxhr_drm import DxhrDrm


class SectionHeader:
    __slots__ = (
        "file_name",
        "len_data",
        "len_relocs",
        "section_type",
        "section_subtype",
        "flags",
        "section_id",
        "specialization",
        "endian",
        "unknown_05",
        "unknown_06",
    )
    _header_format: str = "LBBHLLL"  # noqa

    def __init__(self):
        self.file_name: Optional[str] = None

        self.len_data: int = -1
        self.len_relocs: int = -1
        self.section_type: SectionType = SectionType.unknown
        self.section_subtype: SectionSubtype = SectionSubtype.unknown
        self.flags: int = -1
        self.section_id: int = -1
        self.specialization: int = 0
        self.endian: str = "<"

        self.unknown_05: int = -1
        self.unknown_06: int = -1

    def write(self):
        return struct.pack(
            f"{self.endian}{self._header_format}",
            self.len_data,
            self.section_type.value,
            self.unknown_05,
            self.unknown_06,
            self.flags,
            self.section_id,
            self.specialization,
        )

    @classmethod
    def from_kaitai_struct(cls, kaitai: DxhrDrm.Drm.SectionHeader, endian: str = "<"):
        obj = cls()
        obj.len_data = kaitai.len_data
        obj.len_relocs = kaitai.len_relocs
        obj.section_type = kaitai.type
        obj.section_subtype = kaitai.section_subtype
        obj.flags = kaitai.flags
        obj.section_id = kaitai.sec_id
        obj.specialization = kaitai.spec
        obj.unknown_05 = kaitai.unk05
        obj.unknown_06 = kaitai.unk06
        obj.endian = endian

        return obj

    def __str__(self):
        return f"SectionHeader: {self.section_type.name} ({self.section_id:08X})"

    def __eq__(self, other):
        return (self.section_id == other.section_id) and (
            self.section_type == other.section_type
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class Section:
    __slots__ = ("header", "resolvers", "data", "reloc_data", "ofs_start")

    def __init__(self):
        self.header: Optional[SectionHeader] = None
        self.resolvers: List = []
        self.data: bytes = b""
        self.ofs_start: int = -1
        self.reloc_data: bytes = b""

        # self.PayloadOffset: int = -1

    def __eq__(self, other):
        return (self.data == other.data) and (self.header == other.header)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        if self.header.file_name is not None:
            return self.header.file_name
        else:
            return f"{self.header.section_type.name} {self.header.section_subtype.name} ({self.header.section_id})"

    @classmethod
    def from_kaitai_struct(cls, kaitai: DxhrDrm.Drm.Section):
        obj = cls()
        obj.data = kaitai.payload
        obj.ofs_start = kaitai.start_offs + len(kaitai.align)
        obj.reloc_data = kaitai.relocs
        return obj
