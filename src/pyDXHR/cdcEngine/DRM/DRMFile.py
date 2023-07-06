import struct
from typing import List, Tuple, Optional

from pyDXHR.cdcEngine.DRM.Section import SectionHeader
from pyDXHR.cdcEngine.DRM.Section import Section as Sec
from pyDXHR.cdcEngine.DRM.Resolver import deserialize_resolver_list
from pyDXHR.cdcEngine.DRM import CompressedDRM
from pyDXHR.cdcEngine.DRM import Section
from pyDXHR.cdcEngine.DRM.Reference import Reference

from pyDXHR.utils import Endian
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType, SectionSubtype


class DRMHeader:
    def __init__(self):
        self.Endian = Endian.Little
        self.Version: int = 0
        self.DRMDependencies: list = []
        self.OBJDependencies: list = []
        self.Flags: int = 0
        self.RootSection: int = 0
        self.SectionHeaders: List[SectionHeader] = []

        self._len_drm_deps: int = 0
        self._len_obj_deps: int = 0
        self._unknown0c: int = 0
        self._unknown10: int = 0

    def serialize(self):
        blob = b''

        blob += struct.pack(f"{self.Endian.value}8L",
                            self.Version,
                            self._len_drm_deps,
                            self._len_obj_deps,
                            self._unknown0c,
                            self._unknown10,
                            self.Flags,
                            len(self.SectionHeaders),
                            self.RootSection
                            )

        # section headers
        # TODO

        # pad the end bits so that it's 16-aligned
        # blob += b'\x00' * (16 - (len(blob) % 16))

        return blob

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
            self._len_drm_deps, self._len_obj_deps, \
            self._unknown0c, self._unknown10, \
            self.Flags, \
            len_sections, self.RootSection = struct.unpack_from(f"{self.Endian.value}8L", header_data, offset=0)

        self.SectionHeaders = Section.deserialize_section_headers(
            drm_header=header_data,
            len_sections=len_sections,
            endian=self.Endian
        )

        cursor = (4 * 8)+(20 * len_sections)
        self.OBJDependencies = header_data[cursor:cursor+self._len_obj_deps].decode("ascii").strip("\x00")
        if len(self.OBJDependencies):
            self.OBJDependencies = self.OBJDependencies.split("\x00")
        else:
            self.OBJDependencies = []

        cursor += self._len_obj_deps
        self.DRMDependencies = header_data[cursor:cursor+self._len_drm_deps].decode("ascii").strip("\x00")
        if len(self.DRMDependencies):
            self.DRMDependencies = self.DRMDependencies.split("\x00")
        else:
            self.DRMDependencies = []

        cursor += self._len_drm_deps
        return (cursor + 15) & ~15
        # return cursor


class DRM:
    def __init__(self):
        self.Header = DRMHeader()
        self.Sections: list = []
        self.SectionData: List[bytes] = []

    def lookup_section_subtype(self, section_subtype: SectionSubtype, section_id: Optional[int] = None):
        if self.Sections:
            return [sec for sec in self.Sections if sec.Header.SectionSubtype.value == section_subtype.value]

    def lookup_section(self, section_type: SectionType, section_id: int):
        # ugly af, but it's not like it's used often...
        if self.Sections:
            for sec in self.Sections:
                if sec.Header.SectionType.value == section_type.value and sec.Header.SecId == section_id:
                    return sec

        return None
        # [sec for sec in self.Sections if sec.Header.SectionType == SectionType.DTPData]

    def lookup_reference(self, section_type: SectionType, section_id: int):
        sec = self.lookup_section(section_type, section_id)
        if sec:
            return Reference.from_drm_section(drm=self, section=sec)
        else:
            return None

    def to_gltf(self):
        raise NotImplementedError

    def deserialize(self,
                    data: bytes,
                    header_only: bool = False,
                    merge_generic_sections: bool = False,
                    archive: Optional = None):
        from pyDXHR.cdcEngine.Archive import Archive, ArchivePlatform

        magic, = struct.unpack(">L", data[0:4])

        if magic != CompressedDRM.Magic:
            return False

        from pyDXHR.KaitaiGenerated.DRM import DxhrDrm as KaitaiDRM
        block_data = CompressedDRM.decompress(data, header_only=header_only, return_as_bytes=True)
        kaitai_drm = KaitaiDRM.from_bytes(block_data)

        arc = None
        if archive is not None:
            if archive.platform.value in ArchivePlatform.has_complete_file_lists():
                arc: Optional[Archive] = archive

        if kaitai_drm.version == 0x15:
            self.Header.Endian = Endian.Little
        else:
            self.Header.Endian = Endian.Big
        self.Header.Version = 0x15

        self.Header.DRMDependencies = kaitai_drm.drm_data.drm_dependencies.split("\x00")
        self.Header.OBJDependencies = kaitai_drm.drm_data.obj_dependencies.split("\x00")
        self.Header.RootSection = kaitai_drm.drm_data.root_section
        self.Header.Flags = kaitai_drm.drm_data.flags

        self.Header.SectionHeaders = []
        for head in kaitai_drm.drm_data.section_headers:
            header = SectionHeader()
            header.DataSize = head.len_data
            header.SectionType = SectionType(head.type.value)
            header.Flags = head.flags
            header.SecId = head.sec_id
            header.Language = head.spec
            header.Endian = self.Header.Endian
            header._unk05 = head.unk05
            header._unk06 = head.unk06
            self.Header.SectionHeaders.append(header)

            if arc:
                if header.SecId != 0:
                    if header.SectionType == SectionType.RenderResource:
                        header.Name = arc.texture_list.get(header.SecId)
                    elif header.SectionType == SectionType.Animation:
                        header.Name = arc.animation_list.get(header.SecId)
                    elif header.SectionType == SectionType.FMODSoundBank:
                        header.Name = arc.sound_effects_list.get(header.SecId)
                    elif header.SectionType == SectionType.Object:
                        pass
                        # header.Name = arc.objects.get(header.SecId)
                    else:
                        header.Name = arc.section_list.get(header.SecId)

        for idx, sec in enumerate(kaitai_drm.drm_data.sections):
            section = Sec()
            section.Resolvers = deserialize_resolver_list(
                data=sec.relocs,
                header_list=self.Header.SectionHeaders,
                section_data=sec.payload,
                endian=self.Header.Endian
            )

            section.Header = self.Header.SectionHeaders[idx]
            section.Data = sec.payload
            self.Sections.append(section)
            self.SectionData.append(section.Header.serialize() + sec.relocs + sec.payload)

        return True


        if magic == CompressedDRM.Magic:
            block_data = CompressedDRM.decompress(data, header_only=header_only)
        else:
            return False

        breakpoint()

        if merge_generic_sections:
            # the notes in the xnalara script mention that a generic section type just means that it's supposed
            # to continue from the previous section. but i havent been able to recreate that. so...
            data = CompressedDRM.rebuild_aligned(block_data)
            header_cursor_end = self.Header.deserialize(data)

            section_data = data[header_cursor_end:]

            l = [(sec_header.SectionType == SectionType.Generic, sec_header)
                 for sec_header in self.Header.SectionHeaders]

            ll = []
            for idx, (is_gen, sec_header) in enumerate(l):
                if not is_gen:
                    ll.append(idx)

            lll = [self.Header.SectionHeaders[p:c] for p, c in zip(ll, ll[1:])]

            llll = []
            headers = []
            for i in lll:
                if len(i) > 1:
                    data_size = sum([h.DataSize for h in i])
                    header_size = sum([h.HeaderSize for h in i])
                    llll.append((i[0], data_size, header_size))

                else:
                    llll.append((i[0], i[0].DataSize, i[0].HeaderSize))

                headers.append(i[0])

            if not header_only:
                self.Sections, self.SectionData = Section.from_drm_sizes(
                    block_data=section_data,
                    size_data=llll,
                    header_list=headers,
                    drm_flag=self.Header.Flags,
                    endian=self.Header.Endian
                )

        try:
            # TODO: this should be revised to handle large unit DRMs, particularly det_city_sarif from the ps3 version
            # * the first block is not necessarily the *entire* DRM header

            self.Header.deserialize(block_data[0])

            if not header_only:
                self.Sections, self.SectionData = Section.from_drm_blocks(
                    drm_block_list=block_data[1:],
                    # drm_block_list=block_data,
                    sec_header_list=self.Header.SectionHeaders,
                    drm_flag=self.Header.Flags,
                    endian=self.Header.Endian
                )
        except Exception as e:
            print(e)
            return False
        else:
            return True

    def serialize(self):
        blob = struct.pack(f">L", CompressedDRM.Magic)
        blob += self.Header.serialize()

        # TODO

        return blob

    def __getitem__(self, item: SectionSubtype | SectionSubtype):
        # TODO: generalize this. type checks aren't working??
        if isinstance(item, SectionType):
            return [sec for sec in self.Sections if sec.Header.SectionType == item]
        else:
            return [sec for sec in self.Sections if sec.Header.SectionSubtype == item]

    # TODO: hahaha clean this shit up
    def filter_by_type(self, filter_list: tuple | list):
        if self.Sections:
            return [sec for sec in self.Sections if sec.Header.SectionType in filter_list]
        else:
            return [sec_header for sec_header in self.Header.SectionHeaders if sec_header.SectionType in filter_list]

    def filter_by_subtype(self, filter_list: tuple | list):
        if self.Sections:
            return [sec for sec in self.Sections if sec.Header.SectionSubtype in filter_list]
        else:
            return [sec_header for sec_header in self.Header.SectionHeaders if sec_header.SectionSubtype in filter_list]

    def filter_out_by_type(self, filter_list: tuple | list):
        if self.Sections:
            return [sec for sec in self.Sections if sec.Header.SectionType not in filter_list]
        else:
            return [sec_header for sec_header in self.Header.SectionHeaders if sec_header.SectionType not in filter_list]

    def filter_out_by_subtype(self, filter_list: tuple | list):
        if self.Sections:
            return [sec for sec in self.Sections if sec.Header.SectionSubtype not in filter_list]
        else:
            return [sec_header for sec_header in self.Header.SectionHeaders if sec_header.SectionSubtype not in filter_list]

    def filter_out_dx9_materials(self, materials_only: bool = True):
        # only for pc-w
        if self.Sections:
            return filter_section_list(sec_list=self.Sections, by_type="dx9_materials", materials_only=materials_only)
        else:
            return filter_section_list(sec_header_list=self.Header.SectionHeaders, materials_only=materials_only, by_type="dx9_materials")


def filter_section_list(sec_list: tuple | list | None = None,
                        sec_header_list: tuple | list | None = None,
                        by_type: Optional[str | SectionType | SectionSubtype] = None,
                        **kwargs
                        ):
    if isinstance(by_type, str):
        if by_type == "dx9_materials":
            mat_only = kwargs["materials_only"] if "materials_only" in kwargs else True
            if sec_list:
                return [sec for sec in sec_list if _filter_out_dx9_materials(sec.Header, mat_only)]
            else:
                return [sec_header for sec_header in sec_header_list if _filter_out_dx9_materials(sec_header, mat_only)]
    if isinstance(by_type, SectionType):
        action = kwargs["action"] if "action" in kwargs else "include"
        if action == "include":
            if sec_list:
                return [sec for sec in sec_list if sec.Header.SectionType == by_type]
            else:
                return [sec_header for sec_header in sec_header_list if sec_header.SectionType == by_type]
        if action == "remove":
            if sec_list:
                return [sec for sec in sec_list if sec.Header.SectionType != by_type]
            else:
                return [sec_header for sec_header in sec_header_list if sec_header.SectionType != by_type]


def _filter_out_dx9_materials(inp: SectionHeader,
                              keep_only_materials: bool = True):
    if inp.SectionType != SectionType.Material:
        if keep_only_materials:
            return False
        else:
            return True
    else:
        if inp.Language >> 30 != 1:
            return True
        else:
            return False


def filter_out_render_model_buffer(sec_header_list: tuple | list):
    return [sec_header for sec_header in sec_header_list if sec_header.SectionSubtype != SectionSubtype.RenderModelBuffer]
