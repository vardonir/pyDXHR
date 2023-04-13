from __future__ import annotations

import struct
from typing import List, TYPE_CHECKING
from pyDXHR.cdcEngine.DRM.Section import Section
from pyDXHR.cdcEngine.DRM.Resolver import UnknownResolver, LocalDataResolver, RemoteDataResolver, MissingResolver

if TYPE_CHECKING:
    from pyDXHR.cdcEngine.DRM.DRMFile import DRM


class Reference:
    # adapted from https://github.com/rrika/dxhr/blob/main/tools/drm.py#L21
    # i get the concept, but someday i'll figure out what the pancake is going on here...
    def __init__(self, section_list: List[Section], section: Section, offset: int = 0):
        self.section_list = section_list
        self.section = section
        self.offset: int = offset
        self.resolver = None

    @classmethod
    def from_drm_root(cls, drm: DRM, offset: int = 0):
        return cls(section_list=drm.Sections, section=drm.Sections[drm.Header.RootSection], offset=offset)

    @classmethod
    def from_drm_section(cls, drm: DRM, section: Section, offset: int = 0):
        return cls(section_list=drm.Sections, section=section, offset=offset)

    @classmethod
    def from_drm_id(cls, drm: DRM, sec_id: int, offset: int = 0):
        x = [i.Id for i in drm.Header.SectionHeaders].index(sec_id)
        return cls(section_list=drm.Sections, section=drm.Sections[x], offset=offset)

    def __repr__(self):
        return f"Reference {self.section.Header.SecId} : {hex(self.offset)}"

    def attach_unpacked_archive(self, unpacked_archive):
        pass

    def deref(self, offset=0):
        offset += self.offset
        resolver = [res for res in self.section.Resolvers if offset == res.PointerOffset]

        if len(resolver) == 1:
            resolver = resolver[0]
            self.resolver = resolver

            match type(resolver).__qualname__:
                case UnknownResolver.__qualname__:
                    if type(resolver.SectionId).__qualname__ == MissingResolver.__qualname__:
                        return None
                    elif resolver.SectionId:
                        return Reference(self.section_list, self.section_list[resolver.SectionId], 0)
                    else:
                        # there has to be a much less brute force method for this...
                        return MissingResolver(offset)
                        # external_reference = find_external_reference(reference.SectionType, reference.ExtId)
                        # print(f"MISSING REFERENCE U2R")
                        # print(reference.SectionType)
                        # return external_reference
                case LocalDataResolver.__qualname__:
                    reference_offset = resolver.DataOffset
                    local_section_index = self.section_list.index(self.section)
                    return Reference(self.section_list, self.section_list[local_section_index], reference_offset)
                case RemoteDataResolver.__qualname__:
                    reference_offset = resolver.DataOffset
                    remote_section_index = resolver.SectionIndex
                    return Reference(self.section_list, self.section_list[remote_section_index], reference_offset)
        else:
            return None

    def access(self, unpack_format: str, offset=0, swap: bool = False):
        from pyDXHR.utils import byte_swap

        if swap:
            return struct.unpack_from(unpack_format, byte_swap(self.section.Data), self.offset + offset)[0]
        else:
            return struct.unpack_from(unpack_format, self.section.Data, self.offset + offset)[0]

    def add_offset(self, offset=0):
        return Reference(self.section_list, self.section, self.offset + offset)

    def access_array(self, unpack_format: str, arr_len: int, offset=0):
        return struct.Struct(f"<{arr_len}{unpack_format}").unpack_from(self.section.Data, self.offset + offset)

    def access_null_terminated(self, offset=0):
        # "access everything in the data starting from the offset up until it hits a zero"
        offset += self.offset

        try:
            zero = self.section.Data.index(b"\x00", offset)
        except ValueError:
            zero = None

        return self.section.Data[offset:zero]

    def get_string(self, offset=0, encoding="ascii"):
        dat = self.access_null_terminated(offset)
        try:
            dat.decode(encoding)
        except UnicodeDecodeError:
            return None
        else:
            return dat.decode(encoding)
