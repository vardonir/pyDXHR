# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class MultiplexStream(KaitaiStruct):

    class SegmentType(Enum):
        audio = 0
        cinematic = 1
        subtitle = 2
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header = MultiplexStream.Header(self._io, self, self._root)
        self.padding = self._io.read_bytes(1844)
        self.segments = []
        i = 0
        while not self._io.is_eof():
            self.segments.append(MultiplexStream.Segment(self._io, self, self._root))
            i += 1


    class BlockHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.size = self._io.read_u4le()
            self.stream = self._io.read_u4le()
            self.flag = self._io.read_u4le()
            self.unk0c = self._io.read_u4le()


    class SegmentHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = KaitaiStream.resolve_enum(MultiplexStream.SegmentType, self._io.read_u4le())
            self.len_segment = self._io.read_u4le()
            self.unk08 = self._io.read_u4le()
            self.zero = self._io.read_u4le()


    class Segment(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.segment_header = MultiplexStream.SegmentHeader(self._io, self, self._root)
            if self.segment_header.type != MultiplexStream.SegmentType.audio:
                self.data = self._io.read_bytes(self.segment_header.len_segment)

            if self.segment_header.type == MultiplexStream.SegmentType.audio:
                self.blocks = []
                for i in range(self._root.header.len_channel):
                    self.blocks.append(MultiplexStream.Block(self._io, self, self._root))


            self.padding = self._io.read_bytes(((16 - (self._io.pos() % 16)) % 16))


    class Block(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = MultiplexStream.BlockHeader(self._io, self, self._root)
            self.data = self._io.read_bytes(self.header.size)


    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sample_rate = self._io.read_u4le()
            self.loop_start = self._io.read_u4le()
            self.loop_end = self._io.read_u4le()
            self.len_channel = self._io.read_u4le()
            self.reverb_volume = self._io.read_u4le()
            self.start_size_to_load = self._io.read_u4le()
            self.partial_loop = self._io.read_u4le()
            self.len_loop_area = self._io.read_u4le()
            self.has_cinematic = self._io.read_u4le()
            self.has_subtitles = self._io.read_u4le()
            self.len_face_fx = self._io.read_u4le()
            self.offs_loop_start_file = self._io.read_u4le()
            self.offs_loop_start_bundle = self._io.read_u4le()
            self.max_ee_bytes_per_read = self._io.read_u4le()
            self.len_media = self._io.read_f4le()
            self.volume_left = []
            for i in range(12):
                self.volume_left.append(self._io.read_f4le())

            self.volume_right = []
            for i in range(12):
                self.volume_right.append(self._io.read_f4le())

            self.loop_start_samples_to_skip = []
            for i in range(12):
                self.loop_start_samples_to_skip.append(self._io.read_u4le())




