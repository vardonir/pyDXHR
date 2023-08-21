# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class BigfileHeader(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.alignment = self._io.read_u4le()
        self.bigfile_data = BigfileHeader.Bigfile(self._io, self, self._root)

    class Bigfile(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.alignment < 65535
            if _on == True:
                self._is_le = False
            else:
                self._is_le = True
            if not hasattr(self, '_is_le'):
                raise kaitaistruct.UndecidedEndiannessError("/types/bigfile")
            elif self._is_le == True:
                self._read_le()
            elif self._is_le == False:
                self._read_be()

        def _read_le(self):
            self.platform = (self._io.read_bytes(8)).decode(u"ascii")
            self.zeroes = self._io.read_bytes(56)
            self.len_files = self._io.read_u4le()
            self.hash_table = []
            for i in range(self.len_files):
                self.hash_table.append(self._io.read_u4le())

            self.file_headers = []
            for i in range(self.len_files):
                self.file_headers.append(BigfileHeader.Bigfile.FileHeader(self._io, self, self._root, self._is_le))


        def _read_be(self):
            self.platform = (self._io.read_bytes(8)).decode(u"ascii")
            self.zeroes = self._io.read_bytes(56)
            self.len_files = self._io.read_u4be()
            self.hash_table = []
            for i in range(self.len_files):
                self.hash_table.append(self._io.read_u4be())

            self.file_headers = []
            for i in range(self.len_files):
                self.file_headers.append(BigfileHeader.Bigfile.FileHeader(self._io, self, self._root, self._is_le))


        class FileHeader(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/bigfile/types/file_header")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                self.len_uncompressed = self._io.read_u4le()
                self.offset = self._io.read_u4le()
                self.locale = self._io.read_u4le()
                self.len_compressed = self._io.read_u4le()

            def _read_be(self):
                self.len_uncompressed = self._io.read_u4be()
                self.offset = self._io.read_u4be()
                self.locale = self._io.read_u4be()
                self.len_compressed = self._io.read_u4be()




