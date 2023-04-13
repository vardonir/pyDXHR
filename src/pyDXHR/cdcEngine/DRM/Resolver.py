"""
Regarding the BE implementation: it's a bit handwavy, I don't know if it's the correct method, but it works on initial testing

References: 
- https://github.com/rrika/dxhr/blob/main/tools/drm.py
- https://github.com/gibbed/Gibbed.CrystalDynamics/blob/master/projects/Gibbed.DeusEx3.FileFormats/DRM/Resolver.cs
"""

import struct
from typing import List, Optional
from abc import ABC, abstractmethod

from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
from pyDXHR.utils import byte_swap, Endian


class Resolver(ABC):
    def __init__(self):
        self.PointerOffset: int | None = None
        self.DataOffset: int | None = None
        self.SectionIndex: int | None = None
        self.SectionType: int | None = None
        self.SectionId: int | None = None

    @abstractmethod
    def deserialize(self, data, endian: Endian = Endian.Little):
        pass


class LocalDataResolver(Resolver):
    def deserialize(self, data, endian: Endian = Endian.Little):
        if endian == Endian.Big:
            data, = struct.unpack_from(">Q", byte_swap(data.to_bytes(8, "little")))

        self.PointerOffset = ((data & 0x00000000FFFFFFFF) >> 0)
        self.DataOffset = ((data & 0xFFFFFFFF00000000) >> 32)

    def __repr__(self):
        return f'LDR {self.PointerOffset} {self.DataOffset}'


class RemoteDataResolver(Resolver):
    def deserialize(self, data, endian: Endian = Endian.Little):
        if endian == Endian.Big:
            data, = struct.unpack_from(">Q", byte_swap(data.to_bytes(8, "little")))

        self.SectionIndex = (data & 0x0000000000003FFF) >> 00
        self.PointerOffset = (data & 0x0000003FFFFFC000) >> 12
        self.DataOffset = (data & 0xFFFFFFC000000000) >> 38

    def __repr__(self):
        return f"RDR {self.PointerOffset} {self.DataOffset} | {self.SectionIndex}"


class UnknownResolver(Resolver):
    def deserialize(self,
                    data,
                    section_headers: Optional = None,
                    section_data: bytes = b"",
                    endian: Endian = Endian.Little):
        if endian == Endian.Big:
            data, = struct.unpack_from(">L", byte_swap(data.to_bytes(4, "little")))

        self.PointerOffset = ((data & 0x01FFFFFF) >> 0) * 4
        self.SectionType = SectionType(((data & 0xFE000000) >> 25))

        if section_headers and section_data:
            # uh... where did I get this again?
            ext_id, = struct.unpack_from(f"{endian.value}L", section_data, self.PointerOffset)
            self.SectionId = self._find_section_index(section_headers, self.SectionType, ext_id)

    def _find_section_index(self,
                            section_headers,
                            section_type: SectionType,
                            section_id: int):

        for idx, s in enumerate(section_headers):
            if s.SectionType == section_type and s.SecId == section_id:
                return idx
        else:
            return MissingResolver(self.PointerOffset)

    def __repr__(self):
        return f"UR {self.PointerOffset} | {self.SectionType} {self.SectionId}"


class MissingResolver(Resolver):
    def __init__(self, pointer_offset):
        super().__init__()
        self.PointerOffset = pointer_offset

    def __repr__(self):
        return f"MissingResolver {self.PointerOffset}"

    def deserialize(self, data, endian: Endian = Endian.Little):
        raise Exception("whut")


def deserialize_resolver_list(
        data: bytes,
        header_list,
        section_data: bytes,
        endian: Endian = Endian.Little
) -> List[Resolver]:
    resolvers = []

    if len(data):
        local_resolver_count, remote_resolver_count, \
            u2_resolver_count, u3_resolver_count, u4_resolver_count = \
            struct.unpack_from(f"{endian.value}LLLLL", data)

        offset = 4*5
        local_resolver_data = struct.unpack_from(f"{endian.value}{local_resolver_count}Q", data, offset=offset)
        for lr in local_resolver_data:
            l_res = LocalDataResolver()
            l_res.deserialize(lr, endian=endian)
            resolvers.append(l_res)

        offset += local_resolver_count * 8
        remote_resolver_data = struct.unpack_from(f"{endian.value}{remote_resolver_count}Q", data, offset=offset)
        for rr in remote_resolver_data:
            r_res = RemoteDataResolver()
            r_res.deserialize(rr, endian=endian)
            resolvers.append(r_res)

        offset += remote_resolver_count * 8
        u2_resolver_data = struct.unpack_from(f"{endian.value}{u2_resolver_count}L", data, offset=offset)
        for u2r in u2_resolver_data:
            u2_res = UnknownResolver()
            u2_res.deserialize(data=u2r, section_headers=header_list, section_data=section_data, endian=endian)
            resolvers.append(u2_res)

        offset += u2_resolver_count * 4
        assert u3_resolver_count == 0

        u4_resolver_data = struct.unpack_from(f"{endian.value}{u4_resolver_count}L", data, offset=offset)
        for u4r in u4_resolver_data:
            u4_res = UnknownResolver()
            u4_res.deserialize(data=u4r, section_headers=header_list, section_data=section_data, endian=endian)
            resolvers.append(u4_res)

    return resolvers


def find_resolver(resolver_list: List[Resolver],
                  offset: int = 0,
                  unpacked_archive: Optional = None
                  ) -> Resolver:

    found = MissingResolver(offset)
    for res in resolver_list:
        if offset == res.PointerOffset:
            found = res

    if isinstance(found, MissingResolver) and unpacked_archive:
        for res in resolver_list:
            if isinstance(res, UnknownResolver):
                found = find_in_archive(res.SectionType, res.SectionId, unpacked_archive)

    return found


def find_in_archive(section_type: SectionType,
                    section_id: int,
                    unpacked_archive,
                    offset: int = 0):
    from pyDXHR.cdcEngine.DRM.DRMFile import DRM
    if len(unpacked_archive.ArchiveFiles):
        archive_entry = unpacked_archive.SectionHeaders[(section_type, section_id)]

        if len(archive_entry):
            entry_data = unpacked_archive.get_from_hash(archive_entry[0].NameHash)
            drm = DRM()
            drm.deserialize(entry_data)

            for sec in drm.Sections:
                if sec.Header.SectionType == section_type and sec.Header.SecId == section_id:
                    return find_resolver(sec.Resolvers, offset=offset)

        else:
            raise Exception
    else:
        unpacked_archive.unpack()
        return find_in_archive(section_type, section_id, unpacked_archive)
