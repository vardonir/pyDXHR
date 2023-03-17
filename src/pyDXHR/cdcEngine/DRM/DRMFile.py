import struct
from typing import List, Tuple

from pyDXHR.cdcEngine.DRM import CompressedDRM
from cdcEngine.DRM import Section
from cdcEngine.DRM.SectionTypes import SectionType, SectionSubtype
from utils import Endian


class DRMHeader:
    __slots__ = (
        "Endian",
        "Version",
        "DRMDependencies",
        "OBJDependencies",
        "Flags",
        "RootSection",
        "SectionHeaders"
    )

    def __init__(self):
        self.Endian = Endian.Little
        self.Version: int = 0
        self.DRMDependencies: list = []
        self.OBJDependencies: list = []
        self.Flags: int = 0
        self.RootSection: int = 0
        self.SectionHeaders: list = []

    def deserialize(self, header_data: bytes):
        assert len(header_data) > 32

        le_version, = struct.unpack("<L", header_data[0:4])
        be_version, = struct.unpack(">L", header_data[0:4])

        if le_version != 19 and le_version != 21 and be_version != 19 and be_version != 21:
            raise Exception("Invalid format")
        if le_version == 19 and be_version == 19:
            raise Exception("Not supported")

        if le_version == 21:
            self.Endian = Endian.Little
            self.Version = le_version
        elif be_version == 21:
            self.Endian = Endian.Big
            self.Version = be_version

        version, \
            len_drm_dep, len_obj_dep, \
            unknown0C, unknown10, \
            self.Flags, \
            len_sections, self.RootSection = struct.unpack_from(f"{self.Endian.value}8L", header_data, offset=0)

        self.SectionHeaders = Section.deserialize_section_headers(
            drm_header=header_data,
            len_sections=len_sections,
            endian=self.Endian
        )

        cursor = (4 * 8)+(20 * len_sections)
        self.OBJDependencies = header_data[cursor:cursor+len_obj_dep].decode("ascii").strip("\x00")
        if len(self.OBJDependencies):
            self.OBJDependencies = self.OBJDependencies.split("\x00")
        else:
            self.OBJDependencies = []

        cursor += len_obj_dep
        self.DRMDependencies = header_data[cursor:cursor+len_drm_dep].decode("ascii").strip("\x00")
        if len(self.DRMDependencies):
            self.DRMDependencies = self.DRMDependencies.split("\x00")
        else:
            self.DRMDependencies = []


class DRM:
    def __init__(self):
        self.Header = DRMHeader()
        self.Sections: List[Section] = []

    def deserialize(self, data: bytes, header_only: bool = False):
        magic, = struct.unpack(">L", data[0:4])
        if magic == CompressedDRM.Magic:
            block_data = CompressedDRM.decompress(data, header_only=header_only)
        else:
            raise NotImplementedError

        self.Header.deserialize(block_data[0])

        if not header_only:
            self.Sections = Section.from_drm_blocks(
                drm_block_list=block_data[1:],
                sec_header_list=self.Header.SectionHeaders,
                drm_flag=self.Header.Flags,
                endian=self.Header.Endian
            )

    def __getitem__(self, item: SectionSubtype) -> Section:
        # TODO: generalize this. type checks aren't working??
        # if isinstance(item, SectionType):
        #     return [sec for sec in self.Sections if sec.Header.SectionType == item]
        return [sec for sec in self.Sections if sec.Header.SectionSubtype == item]

    # def filter(self, section_type: SectionType | Tuple[SectionType, SectionSubtype]) -> List[Section]:
    #     if isinstance(section_type, SectionType):
    #         return [sec for sec in self.Sections if sec.Header.SectionType == section_type]
    #     if isinstance(section_type, tuple):
    #         return [sec for sec in self.Sections if sec.Header.SectionType == section_type[0] and sec.Header.SectionSubtype == section_type[1]]
    #     else:
    #         raise KeyError

    def filter_out_dx9_materials(self):
        # only for pc-w
        out = []
        for sec in self.Sections:
            if sec.Header.SectionType != SectionType.Material:
                out.append(sec)
            else:
                if sec.Header.Language >> 30 != 1:
                    out.append(sec)

        return out
