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
        self.len_dds = self._io.read_u4le()
        self.flags_dds = self._io.read_u4le()
        self.height = self._io.read_u4le()
        self.width = self._io.read_u4le()
        self.dds_pitch_size = self._io.read_u4le()
        self.depth = self._io.read_u4le()
        self.mipmap_count = self._io.read_u4le()
        self.dds_reserved = self._io.read_bytes((11 * 4))
        self.pixel_format = Dds.PixelFormat(self._io, self, self._root)
        self.caps_flags = self._io.read_bytes(4)
        self.caps2_flags = self._io.read_bytes(4)
        self.caps3 = self._io.read_bytes(4)
        self.caps4 = self._io.read_bytes(4)
        self.reserved = self._io.read_bytes(4)
        self.payload = self._io.read_bytes_full()

    class PixelFormat(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len = self._io.read_u4le()
            self.flag = self._io.read_bytes(4)
            self.four_cc = self._io.read_bytes(4)
            self.rgb_bit_count = self._io.read_u4le()
            self.r_bitmask = self._io.read_u4le()
            self.g_bitmask = self._io.read_u4le()
            self.b_bitmask = self._io.read_u4le()
            self.a_bitmask = self._io.read_u4le()



