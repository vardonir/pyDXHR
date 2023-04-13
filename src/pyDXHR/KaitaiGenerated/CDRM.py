# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class CdrmData(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = self._io.read_bytes(4)
        self.cdrm = CdrmData.Cdrm(self._io, self, self._root)

    class Cdrm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.magic
            if _on == b"\x43\x44\x52\x4D":
                self._is_le = False
            elif _on == b"\x4D\x52\x44\x43":
                self._is_le = True
            if not hasattr(self, '_is_le'):
                raise kaitaistruct.UndecidedEndiannessError("/types/cdrm")
            elif self._is_le == True:
                self._read_le()
            elif self._is_le == False:
                self._read_be()

        def _read_le(self):
            self.version = self._io.read_u4le()
            self.count = self._io.read_u4le()
            self.padding = self._io.read_u4le()
            self.blocks = []
            for i in range(self.count):
                self.blocks.append(CdrmData.Cdrm.Block(self._io, self, self._root, self._is_le))

            self.pad = self._io.read_bytes(self.padding)

        def _read_be(self):
            self.version = self._io.read_u4be()
            self.count = self._io.read_u4be()
            self.padding = self._io.read_u4be()
            self.blocks = []
            for i in range(self.count):
                self.blocks.append(CdrmData.Cdrm.Block(self._io, self, self._root, self._is_le))

            self.pad = self._io.read_bytes(self.padding)

        class BlockData(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/cdrm/types/block_data")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                self.payload = self._io.read_bytes(self._parent.len_packed)
                self.padding = self._io.read_bytes((((16 - self._parent.len_packed) % 16) % 16))

            def _read_be(self):
                self.payload = self._io.read_bytes(self._parent.len_packed)
                self.padding = self._io.read_bytes((((16 - self._parent.len_packed) % 16) % 16))


        class Block(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/cdrm/types/block")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                self.unpack_info = self._io.read_u4le()
                self.len_packed = self._io.read_u4le()

            def _read_be(self):
                self.unpack_info = self._io.read_u4be()
                self.len_packed = self._io.read_u4be()

            @property
            def len_unpacked(self):
                if hasattr(self, '_m_len_unpacked'):
                    return self._m_len_unpacked

                self._m_len_unpacked = (self.unpack_info >> 8)
                return getattr(self, '_m_len_unpacked', None)

            @property
            def compression_type(self):
                if hasattr(self, '_m_compression_type'):
                    return self._m_compression_type

                self._m_compression_type = (self.unpack_info & 255)
                return getattr(self, '_m_compression_type', None)

            @property
            def block_data(self):
                if hasattr(self, '_m_block_data'):
                    return self._m_block_data

                if self._is_le:
                    self._m_block_data = CdrmData.Cdrm.BlockData(self._io, self, self._root, self._is_le)
                else:
                    self._m_block_data = CdrmData.Cdrm.BlockData(self._io, self, self._root, self._is_le)
                return getattr(self, '_m_block_data', None)




