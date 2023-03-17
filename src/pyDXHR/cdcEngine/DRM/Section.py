import struct
from typing import List

from cdcEngine.DRM.CompressedDRM import rebuild_aligned
from cdcEngine.DRM.SectionTypes import SectionType, SectionSubtype
from utils import Endian


class SectionHeader:
    __slots__ = (
        "DataSize",
        "SectionType",
        "Flags",
        "SecId",
        "Language",
        "Endian"
    )

    # noinspection PyPep8Naming
    @property
    def Specialization(self):
        return self.Language

    def __init__(self):
        self.DataSize: int = 0
        self.SectionType: SectionType = SectionType.UnknownSectionType
        self.Flags: int = 0
        self.SecId: int = 0
        self.Language: int = 0
        self.Endian: Endian = Endian.Little

    def deserialize(self, data, endian: Endian = Endian.Little):
        self.Endian = endian
        self.DataSize, section_type, \
            _05, _06, \
            self.Flags, self.SecId, self.Language = struct.unpack_from(f"{endian.value}LBBHLLL", data, offset=0)

        self.SectionType = SectionType(section_type)

    # noinspection PyPep8Naming
    @property
    def IdHexString(self) -> str:
        if self.SecId:
            return f"{self.SecId:x}".rjust(8, '0')
        else:
            return "00000000"

    # noinspection PyPep8Naming
    @property
    def HeaderSize(self):
        return self.Flags >> 8

    # noinspection PyPep8Naming
    @property
    def SectionSubtype(self):
        return SectionSubtype((self.Flags >> 1) & 0x7f)

    def __str__(self):
        return f"Section type: {self.SectionType.name} " \
               f"Data size: {self.DataSize} " \
               f"Id: {hex(self.SecId)}"

    def __eq__(self, other):
        # https://stackoverflow.com/a/4522896
        import operator
        if isinstance(other, self.__class__):
            if self.__slots__ == other.__slots__:
                attr_getters = [operator.attrgetter(attr) for attr in self.__slots__]
                return all(getter(self) == getter(other) for getter in attr_getters)

        return False

    def __ne__(self, other):
        return not self.__eq__(other)


def deserialize_section_headers(drm_header: bytes,
                                len_sections: int,
                                endian: Endian = Endian.Little):
    data = drm_header[4 * 8:]
    sec_header_list = []
    for i in range(len_sections):
        sh = SectionHeader()
        sh.deserialize(data[(20 * i):], endian)
        sec_header_list.append(sh)

    return sec_header_list


class Section:
    __slots__ = (
        "Header",
        "Resolvers",
        "Data",
    )

    def __init__(self):
        self.Header: SectionHeader = SectionHeader()
        # self.Resolvers: List[Resolver] = []
        self.Data: bytes = b''

    def __repr__(self):
        return f"{self.Header.IdHexString} : {self.Header.DataSize} bytes : {self.Header.SectionType.name} | {self.Header.SectionSubtype.name}"

    # noinspection PyPep8Naming
    @property
    def Flags(self):
        return self.Header.Flags & 0xFF

    def __eq__(self, other):
        return (self.Data == other.Data) and (self.Header == other.Header)

    def __ne__(self, other):
        return not self.__eq__(other)


def from_drm_blocks(
        drm_block_list: List[bytes],
        sec_header_list: List[SectionHeader],
        drm_flag: int,
        endian: Endian = Endian.Little
) -> List[Section]:
    block_data = rebuild_aligned(drm_block_list)

    cursor = 0
    sections = []
    for idx, header in enumerate(sec_header_list):
        sec = Section()
        sec.Header = header

        resolver_data = block_data[cursor: cursor + header.HeaderSize]
        cursor += header.HeaderSize

        if drm_flag & 1:
            cursor = (cursor + 15) & ~15

        sec.Data = block_data[cursor: cursor + header.DataSize]
        cursor += header.DataSize

        if drm_flag & 1:
            cursor = (cursor + 15) & ~15

        # NOT IMPLEMENTED IN THIS VERSION
        # sec.Resolvers = deserialize_resolver_list(
        #     data=resolver_data,
        #     header_list=sec_header_list,
        #     section_data=sec.Data,
        #     endian=endian)

        sections.append(sec)

    return sections
