import struct
from typing import List, Optional, Set, Tuple
from pathlib import Path
from PIL import Image

from pyDXHR.cdcEngine.Archive import ArchivePlatform
from pyDXHR.cdcEngine.DRM.Section import Section
from pyDXHR.cdcEngine.DRM.Resolver import find_resolver, MissingResolver
from pyDXHR.cdcEngine.Sections import AbstractSection
from pyDXHR.cdcEngine.Sections.RenderResource import RenderResource, from_library, from_named_textures
from pyDXHR.cdcEngine.DRM.DRMFile import DRM

# ______________________NOTES______________________
# https://forum.xentax.com/viewtopic.php?p=88434#p88434

# -- Example:
# -- main\bigfile\00d3\000002c7.mtl_a
# -- In this example, the mtrl_a files starts with 0x15. This material does not use any texture files (it is some kind of material for color effects or something who knows).
# -- So in this case, you just skip loading materials when you see this.
#
# -- the first 0x14 bytes is a header
# 15 00 00 00 -- number of offset pairs to read
# 00 00 00 00
# 00 00 00 00
# 00 00 00 00
# 09 00 00 00
#
# -- the next data after header is a list of offset pairs
# [0x00]: 4C 00 00 00 - 90 06 00 00
# [0x01]: C8 06 00 00 - 90 00 00 00
# [0x02]: CC 06 00 00 - C0 00 00 00
# [0x03]: D0 06 00 00 - 30 01 00 00
# [0x04]: 50 00 00 00 - F0 06 00 00
# [0x05]: 28 07 00 00 - 80 01 00 00
# [0x06]: 2C 07 00 00 - B0 01 00 00
# [0x07]: 30 07 00 00 - 20 02 00 00
# [0x08]: 58 00 00 00 - 50 07 00 00
# [0x09]: 88 07 00 00 - 70 02 00 00
# [0x0A]: 8C 07 00 00 - A0 02 00 00
# [0x0B]: 90 07 00 00 - 10 03 00 00
# [0x0C]: 5C 00 00 00 - B0 07 00 00
# [0x0D]: E8 07 00 00 - 60 03 00 00
# [0x0E]: EC 07 00 00 - 90 03 00 00
# [0x0F]: F0 07 00 00 - 00 04 00 00
# [0x10]: 68 00 00 00 - 10 08 00 00
# [0x11]: 48 08 00 00 - 50 04 00 00
# [0x12]: 4C 08 00 00 - F0 04 00 00
# [0x13]: 50 08 00 00 - D0 05 00 00
# [0x14]: 6C 00 00 00 - 50 07 00 00

# -- When the type of material is 0x19, this is a material for character models, and it uses a lot of textures.
# -- There are two offset pairs. It is suffice to use the textures from the first pair.
# -- Here is an example of the offsets. In this case pair index 0x09 and 0x13 point
# -- to a list of texture information.
#
# [0x00]: 4C 00 00 00 - 10 0A 00 00
# [0x01]: 48 0A 00 00 - 90 00 00 00
# [0x02]: 4C 0A 00 00 - E0 00 00 00
# [0x03]: 50 0A 00 00 - 60 01 00 00
# [0x04]: 50 00 00 00 - 70 0A 00 00
# [0x05]: A8 0A 00 00 - D0 01 00 00
# [0x06]: AC 0A 00 00 - 20 02 00 00
# [0x07]: B0 0A 00 00 - A0 02 00 00
# [0x08]: 58 00 00 00 - D0 0A 00 00
# [0x09]: E8 0A 00 00 - 90 0C 00 00 (offsets to filenames A)
# [0x0A]: F0 0A 00 00 - F0 0B 00 00
# [0x0B]: 08 0B 00 00 - 10 03 00 00
# [0x0C]: 0C 0B 00 00 - F0 03 00 00
# [0x0D]: 10 0B 00 00 - 00 05 00 00
# [0x0E]: 5C 00 00 00 - 30 0B 00 00
# [0x0F]: 68 0B 00 00 - F0 05 00 00
# [0x10]: 6C 0B 00 00 - 40 06 00 00
# [0x11]: 70 0B 00 00 - C0 06 00 00
# [0x12]: 68 00 00 00 - 90 0B 00 00
# [0x13]: A8 0B 00 00 - 10 0D 00 00 (offsets to filenames B)
# [0x14]: B0 0B 00 00 - 70 0C 00 00
# [0x15]: C8 0B 00 00 - 30 07 00 00
# [0x16]: CC 0B 00 00 - 10 08 00 00
# [0x17]: D0 0B 00 00 - 20 09 00 00
# [0x18]: 6C 00 00 00 - D0 0A 00 00
#
# -- 8 part A textures
# 8B 0F 00 00 00 00 00 00 00 00 00 00 20 00 01 00 -- 00000F8B is texture ID, 0x20 is color/spec maps, 0x80 is normal map, 0x2C i think is lightmap, and 0x00 is texture index.
# 8A 0F 00 00 00 00 00 00 00 00 00 00 20 01 01 00 -- 00000F8A is texture ID, 0x01 is texture index
# 54 00 00 00 00 00 00 00 00 00 00 00 20 02 01 00  -- 0x02 is texture index
# 16 0C 00 00 00 00 00 00 00 00 00 00 20 03 01 00
# 8A 0F 00 00 00 00 00 00 00 00 00 00 20 04 01 00
# 9E 0F 00 00 00 00 00 00 00 00 00 00 80 05 01 00
# 19 0C 00 00 00 00 80 BF 00 00 00 00 80 06 01 00
# 5D 00 00 00 00 00 00 00 00 00 00 00 2C 07 02 00 -- 0x2C i think is lightmap or something, 0x07 is texture index
#
# -- 3 part B textures
# 19 0C 00 00 00 00 80 BF 00 00 00 00 80 00 01 00
# 9E 0F 00 00 00 00 00 00 00 00 00 00 80 01 01 00
# 8B 0F 00 00 00 00 00 00 00 00 00 00 20 02 01 00

# ______________________NOTES______________________


class Material(AbstractSection):
    def __init__(self, **kwargs):
        self._raw_texture_list = {k: [] for k in range(16)}
        self._texture_library_path: Optional[str | Path] = kwargs.get("texture_library_path", None)
        self._named_textures_path: Optional[str | Path] = kwargs.get("named_textures_path", None)
        self._debug: bool = kwargs.get("debug", False)

        self.ImageDict = {}
        self.Diffuse: List[RenderResource | Image] = []
        self.Normal: List[RenderResource | Image] = []
        self.Specular: List[RenderResource | Image] = []
        self.Mask: List[RenderResource | Image] = []
        self.Blend: List[RenderResource | Image] = []
        self.Cubemap: List[RenderResource | Image] = []
        self.Unknown: List[RenderResource | Image] = []
        self.FlatColors: List[str] = []
        self.LightTex: List[Tuple[str, int]] = []
        self.HasAlpha: bool = False

        self.NeedsChecking: bool = False

        super().__init__(**kwargs)

        if self.section is not None:
            self.MaterialSpec: int = self.section.Header.Language

    def to_wavefront_mtl(self):
        from pyDXHR.utils.wavefront.mtl import cdcMaterial_to_WavefrontMaterial
        return cdcMaterial_to_WavefrontMaterial(self)

    @staticmethod
    def _get_name_from_archive(archive, m_id):
        if archive is not None and archive.platform.value in ArchivePlatform.has_complete_file_lists():
            return archive.section_list[m_id]
        else:
            return "M_" + f"{m_id:x}".rjust(8, '0')

    def to_gltf(self, **kwargs):
        raise NotImplementedError

    def to_json(self):
        return {k: [v[0] for v in vl] for k, vl in self.ImageDict.items() if isinstance(vl, list)}

    def _get_texture_ids(self):

        for idx in range(16):
            # it might just be 8?
            # TODO: find where that note is
            offset = 0x4c + 4 * idx

            submat_blob_data_offset = find_resolver(self.section.Resolvers, offset).DataOffset
            if not submat_blob_data_offset:
                continue

            # out = {}
            # for dep in drm.Header.DRMDependencies:
            #     t_drm = DRM()
            #     t_drm.deserialize(arc.get_from_filename(dep))
            #
            #     for sec in t_drm.Sections:
            #         if sec.Header.SectionType == SectionType.ShaderLib:
            #             out[hex(sec.Header.SecId)] = sec

            texture_resolver = find_resolver(self.section.Resolvers, submat_blob_data_offset + 0x18)

            if isinstance(texture_resolver, MissingResolver):
                continue
            if texture_resolver is None:
                continue

            texture_data_offset = texture_resolver.DataOffset
            # which byte is the real tex count??
            tex_byte1, tex_byte2, tex_count, tex_byte4 = struct.unpack_from(f"{self._endian.value}4B",
                                                                            self.section.Data,
                                                                            submat_blob_data_offset + 0x14)

            if tex_count:
                tb3_data = []
                for i in range(tex_count):
                    tx_off = texture_data_offset + (16 * i)
                    tex_id, *tex_data = struct.unpack_from(f"{self._endian.value}LHHLBBH", self.section.Data, tx_off)
                    tb3_data.append((tex_id, tex_data))

                    # see https://github.com/rrika/cdcEngineDXHR/blob/d3d9/rendering/MaterialData.h#L11
                    # tex_id, lod, cat, fallback_index, slot_index, f = struct.unpack_from(f"{self._endian.value}LfLBBH", self.section.Data, tx_off)

                    self._raw_texture_list[idx].append((tex_id, *tex_data))

    def _deserialize_from_section(self, section):
        super()._deserialize_from_section(section)
        self._load_matlib()

        self._get_texture_ids()
        self._get_textures()
        # self._process_refs()

    def from_drm(self, drm, arc):
        from cdcEngine.DRM.Reference import Reference
        from cdcEngine.DRM.SectionTypes import SectionType
        ref = Reference.from_drm_section(drm=drm, section=self.section, offset=0)

        out = {}
        for dep in drm.Header.DRMDependencies:
            t_drm = DRM()
            t_drm.deserialize(arc.get_from_filename(dep))

            for sec in t_drm.Sections:
                if sec.Header.SectionType == SectionType.ShaderLib:
                    out[sec.Header.SecId] = sec

        def read_submat(submatblob):
            if submatblob is None:
                return (None, None, None, None, [])

            ps = submatblob.deref(0x00)
            vs = submatblob.deref(0x04)
            # hs = submatblob.deref(0x08)
            # ds = submatblob.deref(0x0c)
            tx = submatblob.deref(0x18)

            # p = []
            # if tx and tx.resolver:
            #     tx_off = tx.resolver.DataOffset
            #
            #     tex_byte1, tex_byte2, tex_byte3, tex_count = struct.unpack_from(f"{self._endian.value}4B",
            #                                                                     self.section.Data,
            #                                                                     submatblob.offset + 0x14)
            #
            #     for r_i in range(tex_count):
            #         tex_id, *tex_data = struct.unpack_from(f"{self._endian.value}LHHLBBH", self.section.Data, tx_off)
            #
            #         p.append((tex_id, *tex_data))
            # return (ps, vs, hs, ds, p)

            if isinstance(ps, int) or isinstance(vs, int):
                ps_sec = out.get(ps)
                vs_sec = out.get(vs)

                if ps_sec:
                    from cdcEngine.Sections.ShaderLib import ShaderLib
                    sl = ShaderLib(section=ps_sec)
                    if sl.section.Header.Specialization == 0xBFFFFFFF:
                        breakpoint()

        submats = [
            read_submat(ref.deref(0x4c + 4 * i))
            for i in range(16)
        ]

        breakpoint()

    def debug_print(self):
        print("Material table for ", self.Name)
        print("Material table for ", "M_" + f"{self.section.Header.SecId:x}".rjust(8, '0'))
        # print(f"unk6: {self.section.Header.unk06}")
        for k, v in self._raw_texture_list.items():
            if len(v):
                print("submat ", k)
                for i in v:
                    row_format = "{:>8x}" * len(i)
                    print(row_format.format(*i))

                    # if self._archive.platform.value not in ArchivePlatform.has_complete_file_lists():
                    #     print(row_format.format(*i))
                    # else:
                    #     tex_id = i[0]
                    #     tex_path = self._archive.texture_list[tex_id]
                    #     print(row_format.format(*i), Path(tex_path).stem)

    # def debug_data(self):
    #     return [k for k, v in self._raw_texture_list.items() if len(v) > 0]

    def _load_matlib(self):
        import os
        from dotenv import load_dotenv
        load_dotenv()

        matlib = os.getenv('PYDXHR_MATLIB')
        if matlib:
            self._named_textures_path = os.path.join(matlib, "named_textures.csv")

        texlib = os.getenv("PYDXHR_TEXLIB")
        if texlib:
            self._texture_library_path = texlib

    def _get_textures(self):
        # TODO: handwavy as fck, but idc anymore
        if len(self._raw_texture_list[1]):
            self.HasAlpha = True

        seen = []
        submat_3 = self._raw_texture_list[3]
        for tex_data in submat_3:
            tex_id, tex_info = tex_data[0], tex_data[1:]
            # tex_info = lod, cat, fallback_index, slot_index, f

            if self._texture_library_path:
                tex = (tex_id, from_library(tex_id, self._texture_library_path))
                # tex = tex_data, from_library(tex_id, self.TextureLibrary)
            else:
                tex = tex_id

            if tex_id in seen:
                continue

            seen.append(tex_id)

            if self._named_textures_path:
                tex_type = from_named_textures(tex_id, self._named_textures_path)
                if tex_type is not None:
                    match tex_type:
                        case "diffuse":
                            self.Diffuse.append(tex)
                        case "normal":
                            self.Normal.append(tex)
                        case "mask":
                            self.Mask.append(tex)
                        case "blend":
                            self.Blend.append(tex)
                        case "specular":
                            self.Specular.append(tex)
                        case "cubemap":
                            self.Cubemap.append(tex)
                        case "light":
                            name = from_named_textures(tex_id, self._named_textures_path, get_name_only=True)
                            self.LightTex.append((tex, name))
                        case "flat":
                            name = from_named_textures(tex_id, self._named_textures_path, get_name_only=True)
                            self.FlatColors.append(name.strip())
                        case _:
                            name = from_named_textures(tex_id, self._named_textures_path, get_name_only=True)
                            self.Unknown.append((tex, name))
                    continue

            # if the texture is not in the named textures file...
            match tex_info[1]:
                case 0x4:
                    self.Blend.append(tex)
                    continue
                case 0x5:
                    if self._debug:
                        self.debug_print()

            match tex_info[2]:
                case 0x60:
                    self.Cubemap.append(tex)
                    continue
                case 0x20:
                    self.Diffuse.append(tex)
                    continue
                case 0x40:
                    if self._debug:
                        self.debug_print()
                case 0x2C:  # lightmap apparently???
                    if self._debug:
                        self.debug_print()
                case 0x80:
                    self.Normal.append(tex)
                    continue

            self.Unknown.append(tex)
            seen.append(tex_id)

        self.ImageDict = {
            "diffuse": self.Diffuse,
            "normal": self.Normal,
            "specular": self.Specular,
            "mask": self.Mask,
            "blend": self.Blend,
            "unknown": self.Unknown,
            "colors": self.FlatColors,
            "light": self.LightTex,
            "alpha": 1 if self.HasAlpha else 0
        }

        if len(self.Unknown):
            self.NeedsChecking = True

        for k, v in self.ImageDict.items():
            if k == "colors":
                continue
            if k == "light":
                continue
            if k == "alpha":
                continue

            if len(v) > 1:
                self.NeedsChecking = True
                break


def get_material_ids(sec: Section, offset: int = 0) -> List[int]:
    # of a render model
    mat_resolver = find_resolver(sec.Resolvers, offset=offset)
    if isinstance(mat_resolver, MissingResolver):
        return []

    mat_offset = mat_resolver.DataOffset
    if mat_offset:
        endian = sec.Header.Endian
        count, = struct.unpack_from(f"{endian.value}L", sec.Data, mat_offset)

        mat_ids = []
        for i in range(count):
            id, = struct.unpack_from(f"{endian.value}L", sec.Data, mat_offset+4+4*i)
            mat_ids.append(id)
    else:
        raise Exception

    return mat_ids


def deserialize_drm(
        drm: DRM,
        use_only_dx11: bool = True,
        texture_library: Optional[Path | str] = None
) -> Set[Material]:
    if use_only_dx11:
        mat_list = drm.filter_out_dx9_materials(materials_only=True)
        return {Material(section=mat, texture_library=texture_library) for mat in mat_list}
    else:
        raise NotImplementedError
