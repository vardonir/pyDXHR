from typing import List, Optional
from pyDXHR.DRM import DRM
from pyDXHR.DRM.resolver import Reference
from pyDXHR import SectionType, SectionSubtype

import os
from dotenv import load_dotenv

load_dotenv()


class MaterialTex:
    # struct MaterialTexRef { // = cdc::MaterialData::TextureEntry
    # 	TextureMap *tex;
    # 	float unknown4; // = m_mipLodBias
    # 	uint32_t dword8; // = m_category
    # 	uint8_t fallbackIndex; // = m_type | m_class << 5
    # 	uint8_t slotIndex;
    # 	uint16_t filter;
    # };

    __slots__ = (
        "texture_id",
        "unknown_4",
        "unknown_8",
        "texture_class",
        "slot_index",
        "filter",
        "submat_index",
    )

    @classmethod
    def from_submat_reference(cls, ref: Reference, offset: int = 0):
        obj = cls()
        (
            obj.texture_id,
            obj.unknown_4,
            obj.unknown_8,
            obj.texture_class,
            obj.slot_index,
            obj.filter,
        ) = ref.access(
            "LfLBBH", offset
        )  # noqa
        return obj

    def __repr__(self):
        return f"<MaterialTex {self.texture_id} ({self.texture_class})>"

    def to_json(self):
        return {
            f"{self.texture_id:08X}": [
                self.unknown_4,
                self.unknown_8,
                self.texture_class,
                self.slot_index,
                self.filter,
                self.submat_index,
            ]
        }


class Material:
    def __init__(self):
        self.reference: Optional[Reference] = None
        self.material_tex_list: List[MaterialTex] = []
        self.name: Optional[str] = None
        self.file_name: Optional[str] = None
        self.section_id: Optional[int] = None

    def read(self):
        return self.parse_material_data()

    def parse_material_data(self):
        raise NotImplementedError

    def __repr__(self):
        if self.file_name:
            return f"<{self.__class__.__name__} {self.file_name}>"
        else:
            return f"<{self.__class__.__name__} {self.section_id:08X}>"


class Unknown18(Material):
    @classmethod
    def from_reference(cls, reference: Reference):
        obj = cls()
        obj.reference = reference
        obj.section_id = reference.section.header.section_id
        return obj

    # noinspection PyUnusedLocal
    # pylint: disable=unused-variable
    def parse_material_data(self):
        for i in range(16):
            submat_ref = self.reference.deref(0x4C + 4 * i)
            if submat_ref is None:
                continue

            # useful notes: https://github.com/rrika/dxhr/blob/dad5cfbb0f05f576c96b18268923847d262784fd/tools/cdcmesh.py#L579
            # 0: no pixel shader
            # 1: only concerned with alpha-testing
            # 2: empty in DX11
            # 3: material shading, sampling of light maps happens here
            # 4: renders black
            # 5: empty in DX11
            # 6: empty
            # 7: draw normals
            # 8: copy of 3
            # 9: empty
            # A: empty
            # B: empty
            # C: empty
            # D: empty
            # E: empty
            # F: empty

            # https://github.com/rrika/cdcEngineDXHR/blob/2c035ae85a0745339912341d76aaa8ab8bbfb6e8/rendering/MaterialData.h#L20 ???
            # struct MaterialBlobSub { // = cdc::PassData
            # 	IShaderLib *shaderPixel;
            # 	IShaderLib *shaderVertex;
            # 	IShaderLib *shaderHull;
            # 	IShaderLib *shaderDomain;
            # 	uint32_t dword10;
            #
            # 	uint8_t psByte14;
            # 	uint8_t psRefIndexEndB;
            # 	uint8_t psRefIndexEndA;
            # 	uint8_t psRefIndexBeginB;
            # 	MaterialTexRef *psTextureRef;
            # 	uint32_t psBufferSize;
            # 	char *psBufferData;
            #
            # 	uint8_t vsByte24;
            # 	uint8_t vsRefIndexEndB; // 25
            # 	uint8_t vsRefIndexEndA; // 26
            # 	uint8_t vsRefIndexBeginB; // 27
            # 	MaterialTexRef *vsTextureRef; // 28
            # 	uint32_t vsBufferSize; // 2C
            # 	char *vsBufferData; // 30
            #
            # 	uint8_t psBufferFirstRow; // 34
            # 	uint8_t psBufferNumRows; // 35
            #
            # 	uint8_t vsBufferFirstRow; // 36
            # 	uint8_t vsBufferNumRows; // 37
            #
            # 	ShaderInputSpec *vsLayout[8]; // 38
            # };

            ps = submat_ref.deref(0x00)
            vs = submat_ref.deref(0x04)
            hs = submat_ref.deref(0x08)
            ds = submat_ref.deref(0x0C)

            px_byte14 = submat_ref.access("B", 0x14)
            ps_index_end_b = submat_ref.access("B", 0x15)
            ps_index_end_a = submat_ref.access("B", 0x16)
            ps_index_begin_b = submat_ref.access("B", 0x17)
            ps_texture_ref = submat_ref.deref(0x18)
            ps_buffer_size = submat_ref.access("L", 0x1C)
            ps_buffer_data = submat_ref.deref(0x20)

            vs_byte24 = submat_ref.access("B", 0x24)
            vs_index_end_b = submat_ref.access("B", 0x25)
            vs_index_end_a = submat_ref.access("B", 0x26)
            vs_index_begin_b = submat_ref.access("B", 0x27)
            vs_texture_ref = submat_ref.deref(0x28)
            vs_buffer_size = submat_ref.access("L", 0x2C)
            vs_buffer_data = submat_ref.deref(0x30)

            ps_buffer_first_row = submat_ref.access("B", 0x34)
            ps_buffer_num_rows = submat_ref.access("B", 0x35)

            vs_buffer_first_row = submat_ref.access("B", 0x36)
            vs_buffer_num_rows = submat_ref.access("B", 0x37)

            vs_layout = [submat_ref.deref(0x38 + 4 * j) for j in range(8)]

            # p = []

            if ps_texture_ref:
                for r_i in range(ps_index_end_a):
                    mt = MaterialTex.from_submat_reference(ps_texture_ref, r_i * 0x10)
                    mt.submat_index = i
                    self.material_tex_list.append(mt)

            if vs_texture_ref:
                breakpoint()


def from_drm(drm: DRM) -> List[Material]:
    materials = []

    for sec in drm.sections:
        if sec.header.section_type == SectionType.material:
            if sec.header.section_subtype == SectionSubtype.unknown_18:
                # only the PC version uses the specializations for materials
                if (
                    drm.endian == "<"
                    and (os.getenv("platform", "pc") == "pc")
                    and (os.getenv("read_materials", "dx11") == "dx11")
                    and (sec.header.specialization >> 30 != 1)
                ):
                    continue

                ref = Reference.from_section(drm.sections, sec)
                mat = Unknown18.from_reference(ref)
                mat.file_name = sec.header.file_name
                materials.append(mat)

    return materials
