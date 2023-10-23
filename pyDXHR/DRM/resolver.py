"""
References:
- https://github.com/rrika/dxhr/blob/main/tools/drm.py
- https://github.com/gibbed/Gibbed.CrystalDynamics/blob/master/projects/Gibbed.DeusEx3.FileFormats/DRM/Resolver.cs
"""

import struct
from typing import List, Optional
from abc import ABC, abstractmethod

from pyDXHR import SectionType
from pyDXHR.DRM.Section import SectionHeader


def _byte_swap(data):
    import numpy as np

    a = np.frombuffer(data, dtype=np.uint32)
    aa = a.byteswap()
    bb = aa.tobytes()
    return bb


class Resolver(ABC):
    """Abstract class for resolvers"""

    def __init__(self):
        self.pointer_offset: int | None = None
        self.data_offset: int | None = None
        self.section_index: int | None = None
        self.section_type: int | None = None
        self.section_id: int | None = None
        self.missing_resolver: Optional[MissingResolver] = None

    @abstractmethod
    def deserialize(self, data, endian: str = "<"):
        """Deserialize the resolver data"""
        raise NotImplementedError


class LocalDataResolver(Resolver):
    """Resolvers for data in the same section"""

    def deserialize(self, data, endian: str = "<"):
        if endian == ">":
            (data,) = struct.unpack_from(">Q", _byte_swap(data.to_bytes(8, "little")))

        self.pointer_offset = (data & 0x00000000FFFFFFFF) >> 0
        self.data_offset = (data & 0xFFFFFFFF00000000) >> 32

    def __repr__(self):
        return f"LDR | ptr {self.pointer_offset:08X} | data {self.data_offset:08X}"


class RemoteDataResolver(Resolver):
    """Resolvers for data in the same DRM"""

    def deserialize(self, data, endian: str = "<"):
        # if endian == ">":
        #     (data,) = struct.unpack_from(">Q", _byte_swap(data.to_bytes(8, "little")))

        self.section_index = (data & 0x0000000000003FFF) >> 00
        self.pointer_offset = (data & 0x0000003FFFFFC000) >> 12
        self.data_offset = (data & 0xFFFFFFC000000000) >> 38

    def __repr__(self):
        return f"RDR | ptr {self.pointer_offset:08X} data {self.data_offset:08X} | SecId {self.section_index:08X}"


class UnknownResolver(Resolver):
    def deserialize(
        self,
        data,
        section_headers: Optional = None,
        section_data: bytes = b"",
        endian: str = "<",
    ):
        # if endian == ">":
        #     (data,) = struct.unpack_from(">L", _byte_swap(data.to_bytes(4, "little")))

        self.pointer_offset = ((data & 0x01FFFFFF) >> 0) * 4
        self.section_type = SectionType(((data & 0xFE000000) >> 25))

        if section_headers and section_data:
            (ext_id,) = struct.unpack_from(
                f"{endian}L", section_data, self.pointer_offset
            )
            self.section_index = self._find_section_index(
                section_headers, self.section_type, ext_id
            )

    def _find_section_index(
        self, section_headers, section_type: SectionType, section_id: int
    ):
        """
        I think this was adapted from https://github.com/rrika/dxhr/blob/main/tools/drm.py#L430,
        but I'm not entirely sure anymore...
        """

        for idx, s in enumerate(section_headers):
            if s.section_type == section_type and s.section_id == section_id:
                return idx
        else:
            self.missing_resolver = MissingResolver()
            self.missing_resolver.section_id = section_id
            self.missing_resolver.pointer_offset = self.pointer_offset
            return -1

    def __repr__(self):
        return f"UR | ptr {self.pointer_offset:08X} index {self.section_index:08X} | {SectionType(self.section_type)}"


class UnknownResolver2(UnknownResolver):
    """Overloading the UR for the repr"""

    def __repr__(self):
        return f"U2R | ptr {self.pointer_offset:08X} SecId {self.section_id:08X} | {SectionType(self.section_type)}"


class UnknownResolver4(UnknownResolver):
    """Overloading the UR for the repr"""

    def __repr__(self):
        return f"U4R | ptr {self.pointer_offset:08X} | {SectionType(self.section_type)}"


class MissingResolver(Resolver):
    """I think this is the resolver for "help, your data is in another DRM"?"""

    def __repr__(self):
        return f"MissingResolver | ptr {self.pointer_offset:08X} SecId {self.section_id:08X}"

    def deserialize(self, data, endian: str = "<"):
        raise NotImplementedError


def read_resolver_list(
    resolver_data: bytes,
    header_list: List[SectionHeader],
    section_data: bytes,
    endian: str = "<",
) -> List[Resolver]:
    """
    Read the resolver list from the section data.
    Unknown3 resolvers are parsed for the sake of consistency (and also to check
    if they really are zero).

    There's allegedly a difference between u2 and u4 resolvers, but I don't know enough to comment on it

    :param resolver_data: resolver data from the header
    :param header_list:
    :param section_data:
    :param endian: endian-ess of the data
    :return:
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()
    sort = os.getenv("sort_resolvers", None)

    resolvers = []

    if len(resolver_data):
        (
            local_resolver_count,
            remote_resolver_count,
            u2_resolver_count,
            u3_resolver_count,
            u4_resolver_count,
        ) = struct.unpack_from(f"{endian}5L", resolver_data)

        offset = 4 * 5
        local_resolver_data = struct.unpack_from(
            f"{endian}{local_resolver_count}Q", resolver_data, offset=offset
        )
        l_res_list = []
        for lr in local_resolver_data:
            l_res = LocalDataResolver()
            l_res.deserialize(lr, endian=endian)
            l_res_list.append(l_res)
        if not sort:
            pass
        else:
            if sort == "ptr":
                sorted(l_res_list, key=lambda x: x.pointer_offset)
            elif sort == "data":
                sorted(l_res_list, key=lambda x: x.data_offset)
        resolvers.extend(l_res_list)

        offset += local_resolver_count * 8
        remote_resolver_data = struct.unpack_from(
            f"{endian}{remote_resolver_count}Q", resolver_data, offset=offset
        )
        r_res_list = []
        for rr in remote_resolver_data:
            r_res = RemoteDataResolver()
            r_res.deserialize(rr, endian=endian)
            r_res_list.append(r_res)
        if sort:
            if sort == "ptr":
                sorted(r_res_list, key=lambda x: x.pointer_offset)
            elif sort == "data":
                sorted(r_res_list, key=lambda x: x.data_offset)
        resolvers.extend(r_res_list)

        offset += remote_resolver_count * 8
        u2_resolver_data = struct.unpack_from(
            f"{endian}{u2_resolver_count}L", resolver_data, offset=offset
        )
        u2res_list = []
        for u2r in u2_resolver_data:
            u2_res = UnknownResolver2()
            u2_res.deserialize(
                data=u2r,
                section_headers=header_list,
                section_data=section_data,
                endian=endian,
            )
            u2res_list.append(u2_res)
        if sort and sort == "ptr":
            sorted(u2res_list, key=lambda x: x.pointer_offset)
        resolvers.extend(u2res_list)

        offset += u2_resolver_count * 4
        assert u3_resolver_count == 0

        u4_resolver_data = struct.unpack_from(
            f"{endian}{u4_resolver_count}L", resolver_data, offset=offset
        )
        u4res_list = []
        for u4r in u4_resolver_data:
            u4_res = UnknownResolver4()
            u4_res.deserialize(
                data=u4r,
                section_headers=header_list,
                section_data=section_data,
                endian=endian,
            )
            u4res_list.append(u4_res)
        if sort and sort == "ptr":
            sorted(u4res_list, key=lambda x: x.pointer_offset)
        resolvers.extend(u4res_list)

    return resolvers


class ReferenceSectionNotFound(Exception):
    pass


class Reference:
    def __init__(self):
        from pyDXHR.DRM.Section import Section

        self.section_list = []
        self.section: Optional[Section] = None
        self.offset = 0
        self.resolver = None

        self.endian: str = "<"

    @classmethod
    def from_root(cls, drm, offset: int = 0):
        obj = cls()
        if drm.root_section_index == 0xFFFFFFFF:
            raise ReferenceSectionNotFound

        obj.section_list = drm.sections
        obj.section = drm.sections[drm.root_section_index]
        obj.endian = obj.section.header.endian
        obj.drm = drm
        obj.offset = offset
        return obj

    @classmethod
    def from_section(cls, drm_or_section_list, section, offset: int = 0):
        from pyDXHR.DRM import DRM

        obj = cls()
        if isinstance(drm_or_section_list, DRM):
            obj.section_list = drm_or_section_list.sections
        else:
            obj.section_list = drm_or_section_list
        obj.section = section
        obj.endian = section.header.endian
        obj.offset = offset
        return obj

    @classmethod
    def from_section_index(
        cls, drm_or_section_list, section_index: int, offset: int = 0
    ):
        from pyDXHR.DRM import DRM

        obj = cls()
        if isinstance(drm_or_section_list, DRM):
            obj.section_list = drm_or_section_list.sections
        else:
            obj.section_list = drm_or_section_list

        try:
            obj.section = obj.section_list[section_index]
        except IndexError:
            raise ReferenceSectionNotFound

        obj.endian = obj.section.header.endian
        obj.offset = offset
        return obj

    @classmethod
    def from_section_type(
        cls,
        drm_or_section_list,
        section_id: int,
        section_type: SectionType,
        offset: int = 0,
    ):
        from pyDXHR.DRM import DRM

        obj = cls()
        if isinstance(drm_or_section_list, DRM):
            obj.section_list = drm_or_section_list.sections
        else:
            obj.section_list = drm_or_section_list

        for section in obj.section_list:
            if (
                section.header.section_type == section_type
                and section.header.section_id == section_id
            ):
                obj.section = section
                break

        obj.endian = obj.section.header.endian
        obj.offset = offset
        return obj

    def add(self, offset: int = 0):
        """Add to the current offset"""
        return Reference.from_section(
            self.section_list, self.section, self.offset + offset
        )

    def access(self, unpack_format: str, offset=0):
        """Access numerical data from the section data at the current offset"""
        out = struct.unpack_from(
            f"{self.endian}{unpack_format}", self.section.data, self.offset + offset
        )
        # struct unpack returns a tuple even if there's only one output so...
        if len(out) == 1:
            return out[0]
        else:
            return out

    def access_string(self, offset=0, encoding="utf-8"):
        """
        Equivalent to str-z in kaitai -
        access everything in the data until it hit zero, and then parse that as a string
        """
        dat = self.access_zero(offset)
        try:
            dat.decode(encoding)
        except UnicodeDecodeError:
            return None
        else:
            return dat.decode(encoding)

    def access_zero(self, offset=0):
        """
        Basically, access everything in the section data starting from the offset until a null is encountered
        """
        offset += self.offset

        try:
            zero = self.section.data.index(b"\x00", offset)
        except ValueError:
            zero = None

        return self.section.data[offset:zero]

    def deref(self, offset=0):
        """
        Heavily adapted from https://github.com/rrika/dxhr/blob/main/tools/drm.py#L21

        I think it looks for a resolver in the list of resolvers in the section and returns
        a reference for that section with the given offset, so it's like a pointer that goes
        to a pointer, and eventually it leads to some data. I don't really know, I'm not sure,
        please don't ask me about this function. It works and that's what matters. -v
        """
        offset += self.offset
        try:
            (resolver,) = [
                res for res in self.section.resolvers if offset == res.pointer_offset
            ]
        except ValueError:
            return None
        else:
            self.resolver = resolver
            if type(resolver).__qualname__ == LocalDataResolver.__qualname__:
                reference_offset = resolver.data_offset
                local_section_index = self.section_list.index(self.section)
                obj = Reference.from_section_index(
                    self.section_list, local_section_index, reference_offset
                )
                return obj
            elif type(resolver).__qualname__ == RemoteDataResolver.__qualname__:
                reference_offset = resolver.data_offset
                remote_section_index = resolver.section_index
                obj = Reference.from_section_index(
                    self.section_list, remote_section_index, reference_offset
                )
                return obj
            elif type(resolver).__qualname__ == UnknownResolver2.__qualname__:
                try:
                    return Reference.from_section_index(
                        self.section_list, resolver.section_index
                    )
                except Exception as e:
                    breakpoint()
            elif type(resolver).__qualname__ == UnknownResolver4.__qualname__:
                try:
                    return Reference.from_section_index(
                        self.section_list, resolver.section_index
                    )
                except Exception as e:
                    breakpoint()
            else:
                breakpoint()

        return resolver
