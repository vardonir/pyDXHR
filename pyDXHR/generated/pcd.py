# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Pcd(KaitaiStruct):
    """Texture image type used in the PC version of the game. 
    """

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
        if not self.magic == b"\x50\x43\x44\x39":
            raise kaitaistruct.ValidationNotEqualError(b"\x50\x43\x44\x39", self.magic, self._io, u"/seq/0")
        self.format = KaitaiStream.resolve_enum(Pcd.TextureFormat, self._io.read_u4le())
        self.len_data = self._io.read_u4le()
        self.len_mipmaps = self._io.read_u4le()
        self.width = self._io.read_u2le()
        self.height = self._io.read_u2le()
        self.unk14 = self._io.read_u4le()
        self.unk18 = self._io.read_u4le()
        self.payload = self._io.read_bytes(self.len_data)


