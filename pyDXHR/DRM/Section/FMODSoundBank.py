from typing import Optional
from pyDXHR.DRM import DRM, Section
from pyDXHR import SectionType
import struct


class FMODSoundBank:
    def __init__(self):
        self.byte_data: bytes = b""
        self.fsb_data: bytes = b""
        self.section_id: int = -1
        self.resource_name: Optional[str] = None

    def read(self):
        header = self.byte_data[:0x4]
        # assert header == b'D\xac\x00\x00'

        _, _, _, length_maybe = struct.unpack("4I", self.byte_data[:0x10])
        self.fsb_data = self.byte_data[0x10:]

    @classmethod
    def from_bytes(cls, data: bytes):
        obj = cls()
        obj.byte_data = data
        return obj


def from_section(section: Section) -> FMODSoundBank:
    return FMODSoundBank.from_bytes(section.data)


def from_drm(drm: DRM) -> Optional[FMODSoundBank]:
    for sec in drm.sections:
        if sec.header.section_type == SectionType.fmod:
            return from_section(sec)
    return None
