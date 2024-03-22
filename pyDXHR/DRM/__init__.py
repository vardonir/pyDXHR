"""
Class for reading DRM files, the sections/sec headers, and the resolvers
"""
from pathlib import Path
from kaitaistruct import KaitaiStructError

from pyDXHR.DRM.unpack import unpack_from_byte_data
from pyDXHR.DRM.Section import *
from pyDXHR.Bigfile import Bigfile
from pyDXHR.generated.dxhr_drm import DxhrDrm
from pyDXHR.DRM.Database import emails, ireader, scenario

drm_magic = 0x4344524D
# iReaderDatabase = ireader.IReaderDatabase
# EmailDatabase = email.EMailDatabase
# ScenarioDatabase = scenario.ScenarioDatabase
drm_unpack_from_bytes = unpack_from_byte_data


class InvalidDRMError(Exception):
    """Raised when the input DRM is invalid"""

    pass


class NotCompressedDRMError(Exception):
    """Raised when the input DRM is not compressed"""

    pass


class InvalidDRMVersionException(Exception):
    """Raised when the input DRM invalid"""

    pass


class KaitaiDRM(DxhrDrm):
    """Converts the Kaitai generated DRM class into a more usable format"""

    @property
    def is_le(self):
        """Returns whether the DRM is little endian"""
        return self.version < 65535

    @property
    def drm_dependencies(self):
        """Returns a list of DRM dependencies, split based on nulls"""
        drm_deps = self.drm_data.drm_dependencies.strip("\x00").split("\x00")
        if len(drm_deps) == 1 and drm_deps[0] == "":
            return []
        return drm_deps

    @property
    def obj_dependencies(self):
        """Returns a list of object dependencies, split based on nulls"""
        obj_deps = self.drm_data.obj_dependencies.strip("\x00").split("\x00")
        if len(obj_deps) == 1 and obj_deps[0] == "":
            return []
        return obj_deps

    @property
    def root_section_index(self):
        """Returns the index of the root section"""
        return self.drm_data.root_section

    @property
    def sections(self):
        """Returns a list of sections along with the section headers"""
        return zip(self.drm_data.section_headers, self.drm_data.sections)

    @property
    def flags(self):
        """Returns the DRM flag(s?). Not sure what this is used for, but might be useful"""
        return self.drm_data.flags


class DRM:
    """cdcEngine DRM file"""

    def __init__(self) -> None:
        self.name: Optional[str | int] = None
        self.decompressed_bytes: bytes = b""
        self.obj_deps: List[str] = []
        self.drm_deps: List[str] = []
        self.root_section_index: int = -1
        self.flags: int = -1
        self.endian: str = "<"

        self.sections: List[Section] = []

        self._is_open: bool = False

    def section_summary(self):
        summary = {}
        for sec in self.sections:
            if sec.header.section_type.name not in summary:
                summary[sec.header.section_type.name] = 1
            else:
                summary[sec.header.section_type.name] += 1
        return summary

    def get_section_from_id(self, section_id: int):
        for sec in self.sections:
            if sec.header.section_id == section_id:
                return sec

    def __getitem__(self, item):
        return self.sections[item]

    @classmethod
    def from_bigfile(
        cls, drm_name_or_hash: str | int, bigfile: Bigfile, locale: int = 0xFFFFFFFF
    ):
        """Create DRM object from a Bigfile and a filename/hash"""
        try:
            data = bigfile.read(drm_name_or_hash, locale=locale)
        except KeyError:
            data = bigfile.read(drm_name_or_hash + ".drm", locale=locale)

        obj = cls.from_bytes(data)
        if isinstance(drm_name_or_hash, int):
            obj.name = f"{drm_name_or_hash:08X}"
        else:
            obj.name = drm_name_or_hash
        return obj

    @classmethod
    def from_file(cls, file_path: str):
        """
        Create DRM object from an existing DRM file.
        Function is also compatible with .drm files extracted
        using Gibbed's unpacker.
        """
        with open(file_path, "rb") as drm_file:
            compressed_data = drm_file.read()
        obj = cls.from_bytes(compressed_data)
        obj.name = Path(file_path).stem
        return obj

    @classmethod
    def from_bytes(cls, data: bytes, name: str | int = None):
        """
        Create DRM object from a bytes object. If the magic number is not correct,
        it will be assumed that it is a valid decompressed DRM
        """
        obj = cls()
        obj.name = name
        try:
            obj.decompressed_bytes = decompress(data)
        except NotCompressedDRMError:
            obj.decompressed_bytes = data
        return obj

    def open(self):
        """
        Opens and reads the DRM data - starts with reading the header, then the list of section headers,
        then the section data + resolvers. Looping through the sections twice is probably not the
        most efficient approach, but the resolvers need the complete list of sections to that it'll be
        parsed correctly.

        Anyway, it works.
        """
        from pyDXHR.DRM.Section import Section
        from pyDXHR.DRM.resolver import read_resolver_list

        self._is_open = True

        try:
            kt_drm = KaitaiDRM.from_bytes(self.decompressed_bytes)
        except KaitaiStructError:
            raise InvalidDRMError

        self.endian = "<" if kt_drm.is_le else ">"
        self.obj_deps = kt_drm.obj_dependencies
        self.drm_deps = kt_drm.drm_dependencies
        self.root_section_index = kt_drm.root_section_index
        self.flags = kt_drm.flags

        header_list: List[SectionHeader] = [
            SectionHeader.from_kaitai_struct(head, self.endian)
            for head, _ in kt_drm.sections
        ]

        for header, (_, sec) in zip(header_list, kt_drm.sections):
            assert not len(sec.align.strip(b"\x00"))
            assert not len(sec.align2.strip(b"\x00"))

            section = Section.from_kaitai_struct(sec)
            assert len(sec.relocs) == header.len_relocs
            assert len(sec.payload) == header.len_data

            section.header = header
            section.resolvers = read_resolver_list(
                resolver_data=sec.relocs,
                header_list=header_list,
                section_data=sec.payload,
                endian=self.endian,
            )

            self.sections.append(section)

    def parse_filenames(self, bigfile: Bigfile):
        """Parse filenames based on the ids files. Only works with certain versions of the game"""
        try:
            dtp_list = bigfile.read_data_by_name("dtpdata.ids")
            texture_list = bigfile.read_data_by_name("textures.ids")
            waves_list = bigfile.read_data_by_name("waves.ids")
            object_list = bigfile.read_data_by_name("objectlist.ids")
        except Exception:
            raise FileNotFoundError

        dtp_list = {int(i.split(",")[0]): i.split(",")[1].strip() for i in dtp_list.decode("latin1").split("\n")[1:-1]}  # noqa
        texture_list = {int(i.split(",")[0]): i.split(",")[1].strip() for i in texture_list.decode("latin1").split("\n")[1:-1]}  # noqa
        waves_list = {int(i.split(",")[0]): i.split(",")[1].strip() for i in waves_list.decode("latin1").split("\n")[1:-1]}  # noqa
        object_list = {int(i.split(",")[0]): i.split(",")[1].strip() for i in object_list.decode("latin1").split("\n")[1:-1]}  # noqa

        for sec in self.sections:
            if sec.header.section_type == SectionType.render_resource:
                sec.header.file_name = texture_list.get(sec.header.section_id, None)
                continue
            elif sec.header.section_type == SectionType.fmod:
                sec.header.file_name = waves_list.get(sec.header.section_id, None)
                continue
            elif sec.header.section_type == SectionType.object:
                sec.header.file_name = object_list.get(sec.header.section_id, None)
                continue

            sec.header.file_name = dtp_list.get(sec.header.section_id, None)


def decompress(data: bytes):
    """
    DRM decompression method adapted from:
    https://github.com/gibbed/Gibbed.CrystalDynamics
    https://github.com/rrika/dxhr
    """
    import struct
    import zlib
    import numpy as np

    (magic,) = struct.unpack_from(">L", data)

    if magic != drm_magic:
        raise NotCompressedDRMError

    (le_version,) = struct.unpack_from("<L", data, 4)
    (be_version,) = struct.unpack_from(">L", data, 4)
    if le_version != 0 and le_version != 2 and be_version != 2:
        raise InvalidDRMVersionException

    if le_version == 0:
        raise NotImplementedError
    else:
        endian = "<" if le_version == 2 else ">"
        (count,) = struct.unpack_from(f"{endian}L", data, 8)
        (padding,) = struct.unpack_from(f"{endian}L", data, 12)

    start_of_data = 16 + (count * 8) + padding
    block_sizes = np.frombuffer(
        data, dtype=np.dtype(np.uint32).newbyteorder(endian), count=2 * count, offset=16
    ).reshape((count, 2))

    blob_blocks = []
    blob_size = 0

    cursor = start_of_data
    for idx, i in enumerate(block_sizes):
        cursor = (cursor + 0x0F) & (~0x0F)

        unpacked_size = i[0] >> 8
        packed_size = i[1]
        compression_type = i[0] & 0xFF

        block_data = data[cursor : cursor + packed_size]
        cursor += packed_size.item()

        if compression_type == 1:
            if unpacked_size != packed_size:
                raise Exception("Uncompressed data size mismatch")
            assert len(block_data) == unpacked_size

            blob_blocks.append(block_data)
            blob_size += len(block_data)

        elif compression_type == 2:
            decompressed_data = zlib.decompress(block_data)
            assert len(decompressed_data) == unpacked_size
            blob_blocks.append(decompressed_data)
            blob_size += len(decompressed_data)

        else:
            raise Exception("Unknown compression type")

        padding = b"\0" * ((16 - blob_size) & 0xF)

        blob_blocks.append(padding)
        blob_size += len(padding)

    return b"".join(blob_blocks)


# noinspection PyUnusedLocal
def compress(data: bytes):
    """
    This is not needed, since the game will read DRM
    files in a Bigfile even when they're not compressed, but it's
    included here for completeness.
    """
    raise NotImplementedError


if __name__ == "__main__":
    bf = Bigfile.from_env()
    bf.open()

    drm = DRM.from_bigfile(0xAB0AD4A3, bf)
    drm.open()
    breakpoint()
