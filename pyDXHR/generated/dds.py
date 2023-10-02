# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Dds(KaitaiStruct):

    class TextureFormat(Enum):
        a8r8g8b8 = 21
        dxt1 = 827611204
        dxt3 = 861165636
        dxt5 = 894720068
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = self._io.read_bytes(4)
        if not self.magic == b"\x44\x44\x53\x20":
            raise kaitaistruct.ValidationNotEqualError(b"\x44\x44\x53\x20", self.magic, self._io, u"/seq/0")
        self.len_header = self._io.read_bytes(4)
        if not self.len_header == b"\x7C\x00\x00\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x7C\x00\x00\x00", self.len_header, self._io, u"/seq/1")
        self.flags = self._io.read_u4le()
        self.height = self._io.read_u4le()
        self.width = self._io.read_u4le()
        self.pitch = self._io.read_u4le()
        self.depth = self._io.read_u4le()
        self.len_mipmaps = self._io.read_u4le()
        self.zeros_20 = self._io.read_bytes(44)
        self.thirty_two = self._io.read_bytes(4)
        if not self.thirty_two == b"\x20\x00\x00\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x20\x00\x00\x00", self.thirty_two, self._io, u"/seq/9")
        self.pixel_fmt = self._io.read_u4le()
        self.four_cc = KaitaiStream.resolve_enum(Dds.TextureFormat, self._io.read_u4le())
        self.pixel_size = self._io.read_u4le()
        self.pixel_bitmasks = self._io.read_u4le()
        self.dw_caps_1 = self._io.read_u4le()
        self.dw_caps_2 = self._io.read_u4le()
        self.dw_caps_3 = self._io.read_u4le()
        self.dw_caps_4 = self._io.read_u4le()
        self.zeros_70 = self._io.read_bytes(16)
        self.payload = self._io.read_bytes_full()


