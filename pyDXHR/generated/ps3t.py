# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Ps3t(KaitaiStruct):
    """Texture image type used in the PS3 version of the game.
    """

    class TextureFormat(Enum):
        a8r8g8b8 = 133
        dxt1 = 134
        dxt3 = 135
        dxt5 = 136
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = self._io.read_bytes(4)
        if not self.magic == b"\x50\x53\x33\x54":
            raise kaitaistruct.ValidationNotEqualError(b"\x50\x53\x33\x54", self.magic, self._io, u"/seq/0")
        self.len_data = self._io.read_u4be()
        self.unk_8 = self._io.read_u2be()
        self.unk_a = self._io.read_u2be()
        self.format = KaitaiStream.resolve_enum(Ps3t.TextureFormat, self._io.read_u1())
        self.unk_d = self._io.read_u1()
        self.unk_e = self._io.read_u2be()
        self.unk_10 = self._io.read_u4be()
        self.width = self._io.read_u2be()
        self.height = self._io.read_u2be()
        self.unk_18 = self._io.read_u4be()
        self.unk_1c = self._io.read_u4be()
        self.unk_20 = self._io.read_u4be()
        self.payload = self._io.read_bytes(self.len_data)


