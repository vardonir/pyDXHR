# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class RenderModelBuffer(KaitaiStruct):

    class VtxSem(Enum):
        tesselation_normal = 158890429
        packed_ntb = 162649322
        normal = 922084372
        normal2 = 1048535369
        skin_weights = 1223070144
        skin_indices = 1364646099
        binormal = 1688760065
        color2 = 1933504762
        color1 = 2122176035
        texcoord1 = 2199359530
        texcoord2 = 2387916531
        position = 3539458083
        tangent = 4058845635
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = self._io.read_bytes(4)
        self.header = RenderModelBuffer.MeshData(self._io, self, self._root)

    class MeshData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.magic
            if _on == b"\x68\x73\x65\x4D":
                self._is_le = False
            elif _on == b"\x4D\x65\x73\x68":
                self._is_le = True
            if not hasattr(self, '_is_le'):
                raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data")
            elif self._is_le == True:
                self._read_le()
            elif self._is_le == False:
                self._read_be()

        def _read_le(self):
            self.header = RenderModelBuffer.MeshData.MeshHeader(self._io, self, self._root, self._is_le)

        def _read_be(self):
            self.header = RenderModelBuffer.MeshData.MeshHeader(self._io, self, self._root, self._is_le)

        class MeshHeader(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data/types/mesh_header")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                self.flags = self._io.read_u4le()
                self.len_data = self._io.read_u4le()
                self.len_indices = self._io.read_u4le()
                self.bbox_sphere_center = []
                for i in range(4):
                    self.bbox_sphere_center.append(self._io.read_f4le())

                self.bbox_box_min = []
                for i in range(4):
                    self.bbox_box_min.append(self._io.read_f4le())

                self.bbox_bbox_max = []
                for i in range(4):
                    self.bbox_bbox_max.append(self._io.read_f4le())

                self.bbox_sphere_radius = self._io.read_f4le()
                self.dword44 = self._io.read_f4le()
                self.dword48 = self._io.read_f4le()
                self.vs_select4c = self._io.read_u4le()
                self.mat_table = self._io.read_u4le()
                self.ptr_prim_groups = self._io.read_u4le()
                self.ptr_mesh_table = self._io.read_u4le()
                self.ptr_bones_table = self._io.read_u4le()
                self.ptr_indices = self._io.read_u4le()
                self.len_mesh_prim = self._io.read_u2le()
                self.len_mesh_count = self._io.read_u2le()
                self.len_bone_count = self._io.read_u2le()
                self.word6a = self._io.read_u2le()
                self.dword6c = self._io.read_bytes(4)
                if not self.dword6c == b"\xFF\xFF\xFF\xFF":
                    raise kaitaistruct.ValidationNotEqualError(b"\xFF\xFF\xFF\xFF", self.dword6c, self._io, u"/types/mesh_data/types/mesh_header/seq/19")
                self.dword70 = self._io.read_u4le()
                self.dword74 = self._io.read_u4le()
                self.dword78 = self._io.read_u4le()
                self.dword7c = self._io.read_u4le()

            def _read_be(self):
                self.flags = self._io.read_u4be()
                self.len_data = self._io.read_u4be()
                self.len_indices = self._io.read_u4be()
                self.bbox_sphere_center = []
                for i in range(4):
                    self.bbox_sphere_center.append(self._io.read_f4be())

                self.bbox_box_min = []
                for i in range(4):
                    self.bbox_box_min.append(self._io.read_f4be())

                self.bbox_bbox_max = []
                for i in range(4):
                    self.bbox_bbox_max.append(self._io.read_f4be())

                self.bbox_sphere_radius = self._io.read_f4be()
                self.dword44 = self._io.read_f4be()
                self.dword48 = self._io.read_f4be()
                self.vs_select4c = self._io.read_u4be()
                self.mat_table = self._io.read_u4be()
                self.ptr_prim_groups = self._io.read_u4be()
                self.ptr_mesh_table = self._io.read_u4be()
                self.ptr_bones_table = self._io.read_u4be()
                self.ptr_indices = self._io.read_u4be()
                self.len_mesh_prim = self._io.read_u2be()
                self.len_mesh_count = self._io.read_u2be()
                self.len_bone_count = self._io.read_u2be()
                self.word6a = self._io.read_u2be()
                self.dword6c = self._io.read_bytes(4)
                if not self.dword6c == b"\xFF\xFF\xFF\xFF":
                    raise kaitaistruct.ValidationNotEqualError(b"\xFF\xFF\xFF\xFF", self.dword6c, self._io, u"/types/mesh_data/types/mesh_header/seq/19")
                self.dword70 = self._io.read_u4be()
                self.dword74 = self._io.read_u4be()
                self.dword78 = self._io.read_u4be()
                self.dword7c = self._io.read_u4be()


        class MeshTable(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data/types/mesh_table")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                self.min_dist = self._io.read_f4le()
                self.max_dist = self._io.read_f4le()
                self.min_fade_dist = self._io.read_f4le()
                self.max_fade_dist = self._io.read_f4le()
                self.dword10 = self._io.read_u4le()
                self.dword14 = self._io.read_u4le()
                self.dword18 = self._io.read_u4le()
                self.dword1c = self._io.read_u4le()
                self.dword20 = self._io.read_u4le()
                self.dword24 = self._io.read_u4le()
                self.dword28 = self._io.read_u4le()
                self.dword2c = self._io.read_u4le()
                self.len_mesh_parts = self._io.read_u4le()
                self.len_jnt = self._io.read_u4le()
                self.offset_mesh_jntmap = self._io.read_u4le()
                self.offset_to_vtx_buffer = self._io.read_u4le()
                self.static_vertex_buffer = self._io.read_u4le()
                self.dword44 = self._io.read_u4le()
                self.dword48 = self._io.read_u4le()
                self.offset_to_vtx_buffer_info = self._io.read_u4le()
                self.len_vertices = self._io.read_u4le()
                self.start_index_buffer = self._io.read_u4le()
                self.num_triangles = self._io.read_u4le()
                self.dword5c = self._io.read_u4le()

            def _read_be(self):
                self.min_dist = self._io.read_f4be()
                self.max_dist = self._io.read_f4be()
                self.min_fade_dist = self._io.read_f4be()
                self.max_fade_dist = self._io.read_f4be()
                self.dword10 = self._io.read_u4be()
                self.dword14 = self._io.read_u4be()
                self.dword18 = self._io.read_u4be()
                self.dword1c = self._io.read_u4be()
                self.dword20 = self._io.read_u4be()
                self.dword24 = self._io.read_u4be()
                self.dword28 = self._io.read_u4be()
                self.dword2c = self._io.read_u4be()
                self.len_mesh_parts = self._io.read_u4be()
                self.len_jnt = self._io.read_u4be()
                self.offset_mesh_jntmap = self._io.read_u4be()
                self.offset_to_vtx_buffer = self._io.read_u4be()
                self.static_vertex_buffer = self._io.read_u4be()
                self.dword44 = self._io.read_u4be()
                self.dword48 = self._io.read_u4be()
                self.offset_to_vtx_buffer_info = self._io.read_u4be()
                self.len_vertices = self._io.read_u4be()
                self.start_index_buffer = self._io.read_u4be()
                self.num_triangles = self._io.read_u4be()
                self.dword5c = self._io.read_u4be()

            class VtxSemInfo(KaitaiStruct):
                def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                    self._io = _io
                    self._parent = _parent
                    self._root = _root if _root else self
                    self._is_le = _is_le
                    self._read()

                def _read(self):
                    if not hasattr(self, '_is_le'):
                        raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data/types/mesh_table/types/vtx_sem_info")
                    elif self._is_le == True:
                        self._read_le()
                    elif self._is_le == False:
                        self._read_be()

                def _read_le(self):
                    self.u1 = self._io.read_u4le()
                    self.u2 = self._io.read_u4le()
                    self.len_vtx_sem = self._io.read_u2le()
                    self.len_vtx = self._io.read_u1()
                    self.u3 = self._io.read_u1()
                    self.u4 = self._io.read_u4le()
                    self.semantics = []
                    for i in range(self.len_vtx_sem):
                        self.semantics.append(RenderModelBuffer.MeshData.MeshTable.VtxSem(self._io, self, self._root, self._is_le))


                def _read_be(self):
                    self.u1 = self._io.read_u4be()
                    self.u2 = self._io.read_u4be()
                    self.len_vtx_sem = self._io.read_u2be()
                    self.len_vtx = self._io.read_u1()
                    self.u3 = self._io.read_u1()
                    self.u4 = self._io.read_u4be()
                    self.semantics = []
                    for i in range(self.len_vtx_sem):
                        self.semantics.append(RenderModelBuffer.MeshData.MeshTable.VtxSem(self._io, self, self._root, self._is_le))



            class VtxSem(KaitaiStruct):
                def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                    self._io = _io
                    self._parent = _parent
                    self._root = _root if _root else self
                    self._is_le = _is_le
                    self._read()

                def _read(self):
                    if not hasattr(self, '_is_le'):
                        raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data/types/mesh_table/types/vtx_sem")
                    elif self._is_le == True:
                        self._read_le()
                    elif self._is_le == False:
                        self._read_be()

                def _read_le(self):
                    self.sem = self._io.read_u4le()
                    self.offset = self._io.read_u2le()
                    self.type = self._io.read_u1()
                    self.u1 = self._io.read_u1()

                def _read_be(self):
                    self.sem = self._io.read_u4be()
                    self.offset = self._io.read_u2be()
                    self.type = self._io.read_u1()
                    self.u1 = self._io.read_u1()


            @property
            def vtx_sem_info(self):
                if hasattr(self, '_m_vtx_sem_info'):
                    return self._m_vtx_sem_info

                _pos = self._io.pos()
                self._io.seek(self.offset_to_vtx_buffer_info)
                if self._is_le:
                    self._m_vtx_sem_info = RenderModelBuffer.MeshData.MeshTable.VtxSemInfo(self._io, self, self._root, self._is_le)
                else:
                    self._m_vtx_sem_info = RenderModelBuffer.MeshData.MeshTable.VtxSemInfo(self._io, self, self._root, self._is_le)
                self._io.seek(_pos)
                return getattr(self, '_m_vtx_sem_info', None)


        class MeshPrimHeader(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data/types/mesh_prim_header")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                self.vec0 = []
                for i in range(4):
                    self.vec0.append(self._io.read_u4le())

                self.start_index = self._io.read_u4le()
                self.len_triangles = self._io.read_u4le()
                self.dword18 = self._io.read_u4le()
                self.dword1c = self._io.read_u4le()
                self.dword20 = self._io.read_u4le()
                self.dword24 = self._io.read_u4le()
                self.ptr_material = self._io.read_u4le()
                self.dword2c = self._io.read_u4le()
                self.dword30 = self._io.read_u4le()
                self.dword34 = self._io.read_u4le()
                self.dword38 = self._io.read_u4le()
                self.dword3c = self._io.read_u4le()

            def _read_be(self):
                self.vec0 = []
                for i in range(4):
                    self.vec0.append(self._io.read_u4be())

                self.start_index = self._io.read_u4be()
                self.len_triangles = self._io.read_u4be()
                self.dword18 = self._io.read_u4be()
                self.dword1c = self._io.read_u4be()
                self.dword20 = self._io.read_u4be()
                self.dword24 = self._io.read_u4be()
                self.ptr_material = self._io.read_u4be()
                self.dword2c = self._io.read_u4be()
                self.dword30 = self._io.read_u4be()
                self.dword34 = self._io.read_u4be()
                self.dword38 = self._io.read_u4be()
                self.dword3c = self._io.read_u4be()


        @property
        def mesh_table(self):
            if hasattr(self, '_m_mesh_table'):
                return self._m_mesh_table

            _pos = self._io.pos()
            self._io.seek(self.header.ptr_mesh_table)
            if self._is_le:
                self._m_mesh_table = []
                for i in range(self.header.len_mesh_count):
                    self._m_mesh_table.append(RenderModelBuffer.MeshData.MeshTable(self._io, self, self._root, self._is_le))

            else:
                self._m_mesh_table = []
                for i in range(self.header.len_mesh_count):
                    self._m_mesh_table.append(RenderModelBuffer.MeshData.MeshTable(self._io, self, self._root, self._is_le))

            self._io.seek(_pos)
            return getattr(self, '_m_mesh_table', None)

        @property
        def mesh_prim_table(self):
            if hasattr(self, '_m_mesh_prim_table'):
                return self._m_mesh_prim_table

            _pos = self._io.pos()
            self._io.seek(self.header.ptr_prim_groups)
            if self._is_le:
                self._m_mesh_prim_table = []
                for i in range(self.header.len_mesh_prim):
                    self._m_mesh_prim_table.append(RenderModelBuffer.MeshData.MeshPrimHeader(self._io, self, self._root, self._is_le))

            else:
                self._m_mesh_prim_table = []
                for i in range(self.header.len_mesh_prim):
                    self._m_mesh_prim_table.append(RenderModelBuffer.MeshData.MeshPrimHeader(self._io, self, self._root, self._is_le))

            self._io.seek(_pos)
            return getattr(self, '_m_mesh_prim_table', None)

        @property
        def indices(self):
            if hasattr(self, '_m_indices'):
                return self._m_indices

            _pos = self._io.pos()
            self._io.seek(self.header.ptr_indices)
            if self._is_le:
                self._m_indices = []
                for i in range(self.header.len_indices):
                    self._m_indices.append(self._io.read_u2le())

            else:
                self._m_indices = []
                for i in range(self.header.len_indices):
                    self._m_indices.append(self._io.read_u2be())

            self._io.seek(_pos)
            return getattr(self, '_m_indices', None)



