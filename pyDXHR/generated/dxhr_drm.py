# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class DxhrDrm(KaitaiStruct):
    """Parser for decompressed DRM files used in Crystal Engine games. Tested on
    DRMs from Deus Ex Human Revolution, PC and PS3. Adapted from
    Gibbed.CrystalDynamics code, TheIndra55's cdcResearch notes,
    rrika's cdcEngineDXHR, and many others.
    """

    class SectionType(Enum):
        unknown = -1
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
        unknown = -1
        generic = 0
        texture = 5
        unknown_11 = 11
        sound = 13
        fsfx = 16
        lights = 17
        unknown_18 = 18
        unknown_20 = 20
        unknown_21 = 21
        render_terrain = 24
        unknown_25 = 25
        render_model = 26
        render_model_buffer = 27
        unknown_28 = 28
        unknown_30 = 30
        unknown_32 = 32
        fxfxa = 34
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
        self.version = self._io.read_u4le()
        self.drm_data = DxhrDrm.Drm(self._io, self, self._root)

    class Drm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.version < 65535
            if _on == True:
                self._is_le = True
            else:
                self._is_le = False
            if not hasattr(self, '_is_le'):
                raise kaitaistruct.UndecidedEndiannessError("/types/drm")
            elif self._is_le == True:
                self._read_le()
            elif self._is_le == False:
                self._read_be()

        def _read_le(self):
            self.len_drm_dependencies = self._io.read_u4le()
            self.len_obj_dependencies = self._io.read_u4le()
            self.unk0c = self._io.read_u4le()
            self.unk10 = self._io.read_u4le()
            self.flags = self._io.read_u4le()
            self.len_sections = self._io.read_u4le()
            self.root_section = self._io.read_u4le()
            self.section_headers = []
            for i in range(self.len_sections):
                self.section_headers.append(DxhrDrm.Drm.SectionHeader(i, self._io, self, self._root, self._is_le))

            self.obj_dependencies = (self._io.read_bytes(self.len_obj_dependencies)).decode(u"ascii")
            self.drm_dependencies = (self._io.read_bytes(self.len_drm_dependencies)).decode(u"ascii")
            self.sections = []
            for i in range(self.len_sections):
                self.sections.append(DxhrDrm.Drm.Section(i, self._io.pos(), self._io, self, self._root, self._is_le))


        def _read_be(self):
            self.len_drm_dependencies = self._io.read_u4be()
            self.len_obj_dependencies = self._io.read_u4be()
            self.unk0c = self._io.read_u4be()
            self.unk10 = self._io.read_u4be()
            self.flags = self._io.read_u4be()
            self.len_sections = self._io.read_u4be()
            self.root_section = self._io.read_u4be()
            self.section_headers = []
            for i in range(self.len_sections):
                self.section_headers.append(DxhrDrm.Drm.SectionHeader(i, self._io, self, self._root, self._is_le))

            self.obj_dependencies = (self._io.read_bytes(self.len_obj_dependencies)).decode(u"ascii")
            self.drm_dependencies = (self._io.read_bytes(self.len_drm_dependencies)).decode(u"ascii")
            self.sections = []
            for i in range(self.len_sections):
                self.sections.append(DxhrDrm.Drm.Section(i, self._io.pos(), self._io, self, self._root, self._is_le))


        class Section(KaitaiStruct):
            """Section (relocs + payload) data.
            """
            def __init__(self, idx, start_offs, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self.idx = idx
                self.start_offs = start_offs
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/drm/types/section")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                if (self._parent.flags & 1) == 1:
                    self.align = self._io.read_bytes(((16 - (self._io.pos() % 16)) % 16))

                self.relocs = self._io.read_bytes(self._parent.section_headers[self.idx].len_relocs)
                if (self._parent.flags & 1) == 1:
                    self.align2 = self._io.read_bytes(((16 - (self._io.pos() % 16)) % 16))

                self.payload = self._io.read_bytes(self._parent.section_headers[self.idx].len_data)

            def _read_be(self):
                if (self._parent.flags & 1) == 1:
                    self.align = self._io.read_bytes(((16 - (self._io.pos() % 16)) % 16))

                self.relocs = self._io.read_bytes(self._parent.section_headers[self.idx].len_relocs)
                if (self._parent.flags & 1) == 1:
                    self.align2 = self._io.read_bytes(((16 - (self._io.pos() % 16)) % 16))

                self.payload = self._io.read_bytes(self._parent.section_headers[self.idx].len_data)


        class SectionHeader(KaitaiStruct):
            def __init__(self, idx, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self.idx = idx
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/drm/types/section_header")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                self.len_data = self._io.read_u4le()
                self.type = KaitaiStream.resolve_enum(DxhrDrm.SectionType, self._io.read_u1())
                self.unk05 = self._io.read_u1()
                self.unk06 = self._io.read_u2le()
                self.flags = self._io.read_u4le()
                self.sec_id = self._io.read_u4le()
                self.spec = self._io.read_u4le()

            def _read_be(self):
                self.len_data = self._io.read_u4be()
                self.type = KaitaiStream.resolve_enum(DxhrDrm.SectionType, self._io.read_u1())
                self.unk05 = self._io.read_u1()
                self.unk06 = self._io.read_u2be()
                self.flags = self._io.read_u4be()
                self.sec_id = self._io.read_u4be()
                self.spec = self._io.read_u4be()

            @property
            def len_relocs(self):
                if hasattr(self, '_m_len_relocs'):
                    return self._m_len_relocs

                self._m_len_relocs = ((self.flags & 4294967040) >> 8)
                return getattr(self, '_m_len_relocs', None)

            @property
            def section_subtype(self):
                if hasattr(self, '_m_section_subtype'):
                    return self._m_section_subtype

                self._m_section_subtype = KaitaiStream.resolve_enum(DxhrDrm.SectionSubtype, ((self.flags >> 1) & 127))
                return getattr(self, '_m_section_subtype', None)




