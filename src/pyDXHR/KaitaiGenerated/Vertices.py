# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class VertexInfo(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.u1 = self._io.read_u4le()
        self.u2 = self._io.read_u4le()
        self.len_vtxsem = self._io.read_u2le()
        self.len_vtx = self._io.read_u2le()
        self.u3 = self._io.read_u4le()
        self.vtxsem = []

        for i in range(self.len_vtxsem):
            self.vtxsem.append(VertexInfo.VertexSemantic(self._io, self, self._root))


    class VertexSemantic(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sem = self._io.read_u4le()
            self.offset = self._io.read_u2le()
            self.type = self._io.read_u2le()



