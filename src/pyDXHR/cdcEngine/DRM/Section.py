import struct
from copy import copy
from typing import List, Optional, TYPE_CHECKING, Tuple

import pyDXHR.cdcEngine.DRM.CompressedDRM
import pyDXHR.cdcEngine.DRM.Resolver
from pyDXHR.utils import Endian
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType, SectionSubtype

if TYPE_CHECKING:
    from pyDXHR.cdcEngine.DRM.Resolver import Resolver


class SectionHeader:
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
        return (self.Flags & 0xFFFFFF00) >> 8

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

    def get_file_name(self, archive):
        if self.SectionType == SectionType.RenderResource:
            return archive.texture_list[self.SecId]
        else:
            return archive.section_list[self.SecId]


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
        "Deserialized",
        "Filename",
    )

    def __init__(self):
        self.Header: SectionHeader = SectionHeader()
        self.Resolvers: List[Resolver] = []
        self.Deserialized = None
        self.Filename: Optional[str] = None
        self.Data: bytes = b''

    def __repr__(self):
        if self.Filename:
            return self.Filename

        else:
            return f"{self.Header.IdHexString} : {self.Header.DataSize} bytes : {self.Header.SectionType.name} | {self.Header.SectionSubtype.name}"

    # noinspection PyPep8Naming
    @property
    def Flags(self):
        return self.Header.Flags & 0xFF

    def __eq__(self, other):
        return (self.Data == other.Data) and (self.Header == other.Header)

    def __ne__(self, other):
        return not self.__eq__(other)

    def deserialize(self, archive=None):
        from pyDXHR.cdcEngine.DRM.Sections.Material import Material
        from pyDXHR.cdcEngine.DRM.Sections.RenderResource import RenderResource
        from pyDXHR.cdcEngine.DRM.Sections.DTPData import DTPData
        from pyDXHR.cdcEngine.DRM.Sections.RenderModel import RenderModel
        from pyDXHR.cdcEngine.DRM.Sections.RenderModelBuffer import RenderModelBuffer

        match self.Header.SectionType:
            case SectionType.CollisionMesh:
                pass
            case SectionType.DTPData:
                self.Deserialized = DTPData(section=self, archive=archive)
            case SectionType.RenderMesh:
                match self.Header.SectionSubtype:
                    case SectionSubtype.RenderModel:
                        self.Deserialized = RenderModel(section=self, archive=archive)
                    case SectionSubtype.RenderModelBuffer:
                        self.Deserialized = RenderModelBuffer(section=self, archive=archive)
                    case SectionSubtype.RenderTerrain:
                        pass
                    case _:
                        pass
            case SectionType.RenderResource:
                match self.Header.SectionSubtype:
                    case SectionSubtype.Texture:
                        self.Deserialized = RenderResource(section=self, archive=archive)
                    case _:
                        pass
            case SectionType.Material:
                self.Deserialized = Material(section=self, archive=archive)
            case _:
                pass

        if self.Deserialized:
            self.Filename = self.Deserialized.Name
        return self.Deserialized


def from_drm_sizes(
        block_data: bytes,
        size_data: list,
        header_list: list,
        drm_flag: int,
        endian: Endian = Endian.Little
):
    # an attempt to merge the generic sections... it's not working yet
    cursor = 0
    sections = []
    section_data = []
    for idx, (header, data_size, header_size) in enumerate(size_data):
        sec = Section()
        sec.Header = header
        sec_start = copy(cursor)

        resolver_data = block_data[cursor: cursor + header_size]
        cursor += header_size

        if drm_flag & 1:
            cursor = (cursor + 15) & ~15

        sec.Data = block_data[cursor: cursor + data_size]
        cursor += data_size

        if drm_flag & 1:
            cursor = (cursor + 15) & ~15

        sec_end = copy(cursor)
        sec.Resolvers = pyDXHR.cdcEngine.DRM.Resolver.deserialize_resolver_list(
            data=resolver_data,
            header_list=header_list,
            section_data=sec.Data,
            endian=endian)

        sections.append(sec)
        section_data.append(block_data[sec_start:sec_end])

    return sections, section_data


def from_drm_blocks(
        drm_block_list: List[bytes],
        sec_header_list: List[SectionHeader],
        drm_flag: int,
        endian: Endian = Endian.Little
) -> Tuple[List[Section], List[bytes]]:
    block_data = pyDXHR.cdcEngine.DRM.CompressedDRM.rebuild_aligned(drm_block_list)

    cursor = 0
    sections = []
    section_data = []
    for idx, header in enumerate(sec_header_list):
        sec = Section()
        sec.Header = header
        sec_start = cursor

        # if sec.Header.SectionType == SectionType.Material:
        #     breakpoint()

        resolver_data = block_data[cursor: cursor + header.HeaderSize]
        cursor += header.HeaderSize

        if drm_flag & 1:
            cursor = (cursor + 15) & ~15

        sec.Data = block_data[cursor: cursor + header.DataSize]
        cursor += header.DataSize

        if drm_flag & 1:
            cursor = (cursor + 15) & ~15

        sec.Resolvers = pyDXHR.cdcEngine.DRM.Resolver.deserialize_resolver_list(
            data=resolver_data,
            header_list=sec_header_list,
            section_data=sec.Data,
            endian=endian)

        sec_end = cursor
        sections.append(sec)
        section_data.append(block_data[sec_start:sec_end])

    return sections, section_data
