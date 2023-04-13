# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))


class RenderModelHeaderPC(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = self._io.read_bytes(4)
        if not self.magic == b"\x4D\x65\x73\x68":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x65\x73\x68", self.magic, self._io, u"/seq/0")
        self.unk1 = self._io.read_bytes(4)
        self.len_meshes = self._io.read_u4le()
        self.len_indices = self._io.read_u4le()
        self.u1 = []
        for i in range((((4 + 4) + 4) + 4)):
            self.u1.append(self._io.read_f4le())

        self.zeros = self._io.read_bytes(4)
        if not self.zeros == b"\x00\x00\x00\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x00\x00\x00\x00", self.zeros, self._io, u"/seq/5")
        self.off_mesh_prim = self._io.read_u4le()
        self.off_mesh = self._io.read_u4le()
        self.off_jnt_id = self._io.read_u4le()
        self.off_idx_buffer = self._io.read_u4le()
        self.len_mesh_prim = self._io.read_u2le()
        self.len_mesh = self._io.read_u2le()
        self.len_jnts = self._io.read_u4le()
        self.end_header = self._io.read_bytes(4)
        if not self.end_header == b"\xFF\xFF\xFF\xFF":
            raise kaitaistruct.ValidationNotEqualError(b"\xFF\xFF\xFF\xFF", self.end_header, self._io, u"/seq/13")

# https://github.com/rrika/cdcEngineDXHR/blob/main/rendering/RenderMesh.h#L48
# struct MeshFlags {
# 	uint32_t hasBones : 1;
# 	uint32_t depthLayer : 1;
# };
#
# struct Mesh { // = cdc::ModelData
# 	uint32_t magic;
# 	MeshFlags flags;
# 	uint32_t dword8; // totalDataSize
# 	uint32_t numIndices;
# 	float boundingSphereCenter[4];
# 	float boundingBoxMin[4];
# 	float boundingBoxMax[4];
# 	float boundingSphereRadius;
# 	float dword44;
# 	float dword48;
# 	uint32_t vsSelect4C;
# 	uint32_t matTableMaybe; // 50
# 	PrimGroup *primGroups; // 54
# 	ModelBatch *meshTable; // 58
# 	uint32_t bonesTableMaybe; // 5C
# 	uint32_t indices; // 60
# 	uint16_t primGroupCount; // 64
# 	uint16_t meshCount; // 66
# 	uint16_t boneCountMaybe; // 68
# 	uint16_t word6A;
# 	uint32_t dword6C;
# 	uint32_t dword70; // offset from beginning of struct, patched to pointer
# 	uint32_t dword74;
# 	uint32_t dword78;
# 	uint32_t dword7C;
# };

