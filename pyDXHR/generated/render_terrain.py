# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class RenderTerrain(KaitaiStruct):

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
        self.flags = self._io.read_u4le()
        self.data = RenderTerrain.MeshData(self._io, self, self._root)

    class MeshData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.flags < 65535
            if _on == True:
                self._is_le = True
            else:
                self._is_le = False
            if not hasattr(self, '_is_le'):
                raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data")
            elif self._is_le == True:
                self._read_le()
            elif self._is_le == False:
                self._read_be()

        def _read_le(self):
            self.header = RenderTerrain.MeshData.Header(self._io, self, self._root, self._is_le)

        def _read_be(self):
            self.header = RenderTerrain.MeshData.Header(self._io, self, self._root, self._is_le)

        class VtxBuffer(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data/types/vtx_buffer")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                self.off_vtx_buffer = self._io.read_u4le()
                self.unk1 = self._io.read_u4le()
                self.len_vtx_buffer = self._io.read_u4le()
                self.i_fmt = self._io.read_u4le()

            def _read_be(self):
                self.off_vtx_buffer = self._io.read_u4be()
                self.unk1 = self._io.read_u4be()
                self.len_vtx_buffer = self._io.read_u4be()
                self.i_fmt = self._io.read_u4be()

            @property
            def vertices(self):
                if hasattr(self, '_m_vertices'):
                    return self._m_vertices

                _pos = self._io.pos()
                self._io.seek(self.off_vtx_buffer)
                if self._is_le:
                    self._m_vertices = self._io.read_bytes(0)
                else:
                    self._m_vertices = self._io.read_bytes(0)
                self._io.seek(_pos)
                return getattr(self, '_m_vertices', None)


        class VtxSem(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data/types/vtx_sem")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                self.sem = KaitaiStream.resolve_enum(RenderTerrain.VtxSem, self._io.read_u4le())
                self.offset = self._io.read_u2le()
                self.type = self._io.read_u1()
                self.u1 = self._io.read_u1()

            def _read_be(self):
                self.sem = KaitaiStream.resolve_enum(RenderTerrain.VtxSem, self._io.read_u4be())
                self.offset = self._io.read_u2be()
                self.type = self._io.read_u1()
                self.u1 = self._io.read_u1()


        class VtxSemInfo(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data/types/vtx_sem_info")
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
                    self.semantics.append(RenderTerrain.MeshData.VtxSem(self._io, self, self._root, self._is_le))


            def _read_be(self):
                self.u1 = self._io.read_u4be()
                self.u2 = self._io.read_u4be()
                self.len_vtx_sem = self._io.read_u2be()
                self.len_vtx = self._io.read_u1()
                self.u3 = self._io.read_u1()
                self.u4 = self._io.read_u4be()
                self.semantics = []
                for i in range(self.len_vtx_sem):
                    self.semantics.append(RenderTerrain.MeshData.VtxSem(self._io, self, self._root, self._is_le))



        class Something(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data/types/something")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                self.idk = []
                for i in range(12):
                    self.idk.append(self._io.read_u4le())


            def _read_be(self):
                self.idk = []
                for i in range(12):
                    self.idk.append(self._io.read_u4be())



        class Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data/types/header")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                self.offset_node = self._io.read_u4le()
                self.len_nodes = self._io.read_u4le()
                self.offset_group = self._io.read_u4le()
                self.len_group = self._io.read_u4le()
                self.offset_vtx_buffer_info = self._io.read_u4le()
                self.len_vtx_buffer_info = self._io.read_u4le()
                self.dword1c = self._io.read_u4le()
                self.offset_vb = self._io.read_u4le()
                self.len_vb = self._io.read_u4le()
                self.offset_geom = self._io.read_u4le()
                self.len_geom = self._io.read_u4le()
                self.len_textures = self._io.read_u4le()
                self.ptr_indices = self._io.read_u4le()
                self.len_indices = self._io.read_u4le()
                self.ptr_smth = self._io.read_u4le()
                self.len_smth = self._io.read_u4le()

            def _read_be(self):
                self.offset_node = self._io.read_u4be()
                self.len_nodes = self._io.read_u4be()
                self.offset_group = self._io.read_u4be()
                self.len_group = self._io.read_u4be()
                self.offset_vtx_buffer_info = self._io.read_u4be()
                self.len_vtx_buffer_info = self._io.read_u4be()
                self.dword1c = self._io.read_u4be()
                self.offset_vb = self._io.read_u4be()
                self.len_vb = self._io.read_u4be()
                self.offset_geom = self._io.read_u4be()
                self.len_geom = self._io.read_u4be()
                self.len_textures = self._io.read_u4be()
                self.ptr_indices = self._io.read_u4be()
                self.len_indices = self._io.read_u4be()
                self.ptr_smth = self._io.read_u4be()
                self.len_smth = self._io.read_u4be()


        class Node(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data/types/node")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                self.off_list = self._io.read_u4le()
                self.nrange = self._io.read_u2le()

            def _read_be(self):
                self.off_list = self._io.read_u4be()
                self.nrange = self._io.read_u2be()

            class MeshPrimHeader(KaitaiStruct):
                def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                    self._io = _io
                    self._parent = _parent
                    self._root = _root if _root else self
                    self._is_le = _is_le
                    self._read()

                def _read(self):
                    if not hasattr(self, '_is_le'):
                        raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data/types/node/types/mesh_prim_header")
                    elif self._is_le == True:
                        self._read_le()
                    elif self._is_le == False:
                        self._read_be()

                def _read_le(self):
                    self.start_index = self._io.read_u4le()
                    self.len_triangles = self._io.read_u4le()

                def _read_be(self):
                    self.start_index = self._io.read_u4be()
                    self.len_triangles = self._io.read_u4be()



        class Group(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None, _is_le=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._is_le = _is_le
                self._read()

            def _read(self):
                if not hasattr(self, '_is_le'):
                    raise kaitaistruct.UndecidedEndiannessError("/types/mesh_data/types/group")
                elif self._is_le == True:
                    self._read_le()
                elif self._is_le == False:
                    self._read_be()

            def _read_le(self):
                self.idx_material = self._io.read_u4le()
                self.idx_vb = self._io.read_u4le()
                self.flags = self._io.read_u2le()
                self.unk = self._io.read_u2le()
                self.render_passes = self._io.read_u4le()
                self.instance_texture_indices = []
                for i in range(4):
                    self.instance_texture_indices.append(self._io.read_u4le())


            def _read_be(self):
                self.idx_material = self._io.read_u4be()
                self.idx_vb = self._io.read_u4be()
                self.flags = self._io.read_u2be()
                self.unk = self._io.read_u2be()
                self.render_passes = self._io.read_u4be()
                self.instance_texture_indices = []
                for i in range(4):
                    self.instance_texture_indices.append(self._io.read_u4be())



        @property
        def vtx_buffer(self):
            if hasattr(self, '_m_vtx_buffer'):
                return self._m_vtx_buffer

            _pos = self._io.pos()
            self._io.seek(self.header.offset_vb)
            if self._is_le:
                self._m_vtx_buffer = []
                for i in range(self.header.len_vb):
                    self._m_vtx_buffer.append(RenderTerrain.MeshData.VtxBuffer(self._io, self, self._root, self._is_le))

            else:
                self._m_vtx_buffer = []
                for i in range(self.header.len_vb):
                    self._m_vtx_buffer.append(RenderTerrain.MeshData.VtxBuffer(self._io, self, self._root, self._is_le))

            self._io.seek(_pos)
            return getattr(self, '_m_vtx_buffer', None)

        @property
        def something(self):
            if hasattr(self, '_m_something'):
                return self._m_something

            _pos = self._io.pos()
            self._io.seek(self.header.ptr_smth)
            if self._is_le:
                self._m_something = []
                for i in range(self.header.len_smth):
                    self._m_something.append(RenderTerrain.MeshData.Something(self._io, self, self._root, self._is_le))

            else:
                self._m_something = []
                for i in range(self.header.len_smth):
                    self._m_something.append(RenderTerrain.MeshData.Something(self._io, self, self._root, self._is_le))

            self._io.seek(_pos)
            return getattr(self, '_m_something', None)

        @property
        def vtx_sem_info(self):
            if hasattr(self, '_m_vtx_sem_info'):
                return self._m_vtx_sem_info

            _pos = self._io.pos()
            self._io.seek(self.header.offset_vtx_buffer_info)
            if self._is_le:
                self._m_vtx_sem_info = []
                for i in range(self.header.len_vtx_buffer_info):
                    self._m_vtx_sem_info.append(RenderTerrain.MeshData.VtxSemInfo(self._io, self, self._root, self._is_le))

            else:
                self._m_vtx_sem_info = []
                for i in range(self.header.len_vtx_buffer_info):
                    self._m_vtx_sem_info.append(RenderTerrain.MeshData.VtxSemInfo(self._io, self, self._root, self._is_le))

            self._io.seek(_pos)
            return getattr(self, '_m_vtx_sem_info', None)

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

        @property
        def groups(self):
            if hasattr(self, '_m_groups'):
                return self._m_groups

            _pos = self._io.pos()
            self._io.seek(self.header.offset_group)
            if self._is_le:
                self._m_groups = []
                for i in range(self.header.len_group):
                    self._m_groups.append(RenderTerrain.MeshData.Group(self._io, self, self._root, self._is_le))

            else:
                self._m_groups = []
                for i in range(self.header.len_group):
                    self._m_groups.append(RenderTerrain.MeshData.Group(self._io, self, self._root, self._is_le))

            self._io.seek(_pos)
            return getattr(self, '_m_groups', None)



