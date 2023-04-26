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

    @staticmethod
    def _get_name_from_archive(archive, m_id):
        if archive is not None and archive.platform.value in ArchivePlatform.has_complete_file_lists():
            return archive.section_list[m_id]
        else:
            return "M_" + f"{m_id:x}".rjust(8, '0')

    def to_gltf(self,
                as_library: bool = False,
                library_dir: Optional[Path | str] = None
                ):
        raise NotImplementedError

    def _get_texture_ids(self):

        for idx in range(16):
            offset = 0x4c + 4 * idx

            submat_blob_data_offset = find_resolver(self.section.Resolvers, offset).DataOffset
            if not submat_blob_data_offset:
                continue

            texture_resolver = find_resolver(self.section.Resolvers, submat_blob_data_offset + 0x18)

            if isinstance(texture_resolver, MissingResolver):
                continue
            if texture_resolver is None:
                continue

            texture_data_offset = texture_resolver.DataOffset
            # which byte is the real tex count??
            tex_byte1, tex_byte2, tex_byte3, tex_count = struct.unpack_from(f"{self._endian.value}4B",
                                                                            self.section.Data,
                                                                            submat_blob_data_offset + 0x14)

            if tex_count:
                tb3_data = []
                for i in range(tex_count):
                    tx_off = texture_data_offset + (16 * i)
                    tex_id, *tex_data = struct.unpack_from(f"{self._endian.value}LfLBBH", self.section.Data, tx_off)
                    tb3_data.append((tex_id, tex_data))

                    # see https://github.com/rrika/cdcEngineDXHR/blob/d3d9/rendering/MaterialData.h#L11
                    # tex_id, lod, cat, fallback_index, slot_index, f = struct.unpack_from(f"{self._endian.value}LfLBBH", self.section.Data, tx_off)

                    self._raw_texture_list[idx].append((tex_id, *tex_data))

    def _deserialize_from_section(self, section):
        super()._deserialize_from_section(section)
        self._get_texture_ids()
        self._get_textures()

    def debug_print(self):
        print("Material table for ", "M_" + f"{self.section.Header.SecId:x}".rjust(8, '0'))
        print(f"unk6: {self.section.Header.unk06}")
        for k, v in self._raw_texture_list.items():
            if len(v):
                print("submat ", k)
                for i in v:
                    row_format = "{:>8}" * len(i)
                    print(row_format.format(*i))

                    # if self._archive.platform.value not in ArchivePlatform.has_complete_file_lists():
                    #     print(row_format.format(*i))
                    # else:
                    #     tex_id = i[0]
                    #     tex_path = self._archive.texture_list[tex_id]
                    #     print(row_format.format(*i), Path(tex_path).stem)

    # def debug_data(self):
    #     return [k for k, v in self._raw_texture_list.items() if len(v) > 0]

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
