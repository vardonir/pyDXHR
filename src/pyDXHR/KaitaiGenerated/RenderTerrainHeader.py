# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class RenderTerrainHeader(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    # def _read(self):
    #     self.unk1 = self._io.read_u4le()
    #     self.unk2 = self._io.read_u4le()
    #     self.len_lists = self._io.read_u4le()
    #     self.off_targets = self._io.read_u4le()
    #     self.len_targets = self._io.read_u4le()
    #     self.off_fmtstream = self._io.read_u4le()
    #     self.len_fmts = self._io.read_u2le()
    #     self.unk3 = self._io.read_u2le()
    #     self.unk4 = self._io.read_u4le()
    #     self.off_buffers = self._io.read_u4le()
    #     self.len_buffers = self._io.read_u2le()
    #     self.unk5 = self._io.read_u2le()
    #     self.off_list = self._io.read_u4le()
    #     self.unk6 = self._io.read_u4le()
    #     self.unk7 = self._io.read_u4le()
    #     self.off_indices = self._io.read_u4le()
    #     self.len_indices = self._io.read_u4le()

    def _read(self):
        self.mflags = self._io.read_u4le()
        self.offset_node = self._io.read_u4le()
        self.len_nodes = self._io.read_u4le()
        self.offset_group = self._io.read_u4le()
        self.len_group = self._io.read_u4le()
        self.offset_layout = self._io.read_u4le()
        self.len_layout = self._io.read_u2le()
        self.unk1 = self._io.read_u2le()
        self.dword1c = self._io.read_u4le()
        self.offset_vb = self._io.read_u4le()
        self.len_vb = self._io.read_u2le()
        self.unk2 = self._io.read_u2le()
        self.offset_geom = self._io.read_u4le()
        self.dword2c = self._io.read_u4le()
        self.dword30 = self._io.read_u4le()
        self.offset_indices = self._io.read_u4le()
        self.len_indices = self._io.read_u4le()
        self.dword3c = self._io.read_u4le()
        self.dword40 = self._io.read_u4le()

    # dword3c and dword40:
    # a table of somethingggg (offset dword3c)
    # meta:
    #   id: something
    #   endian: le
    #
    # seq:
    #   - id: s
    #     type: aaa
    #     repeat: expr
    #     repeat-expr: dword40
    #
    # types:
    #   aaa:
    #     seq:
    #       - id: u1
    #         type: u4
    #       - id: u2
    #         type: u4
    #       - id: u3
    #         type: u4
    #       - id: u4
    #         type: u4
    #       - id: u5
    #         type: u4
    #       - id: u6
    #         type: u4
    #       - id: u7
    #         type: u4
    #       - id: u8
    #         type: u4
    #       - id: u9
    #         type: u4
    #       - id: u10
    #         type: u4
    #       - id: u11
    #         type: u4
    #       - id: u12
    #         type: u4
