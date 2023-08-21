# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Enums(KaitaiStruct):
    """enums used in pyDXHR
    """

    class SectionType(Enum):
        generic = 0
        empty = 1
        animation = 2
        render_resource = 5
        fmod = 6
        dtpdata = 7
        script = 8
        shaderlib = 9
        material = 10
        object = 11
        render_mesh = 12
        collision_mesh = 13
        stream_group_list = 14

    class SectionSubtype(Enum):
        generic = 0
        texture = 5
        sound = 13
        unknown_18 = 18
        unknown_20 = 20
        render_terrain = 24
        unknown_25 = 25
        render_model = 26
        render_model_buffer = 27
        unknown_30 = 30
        unknown_36 = 36
        smart_script = 40
        scaleform = 41
        conversation = 42
        camera_shake = 50
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        pass


