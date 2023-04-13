import struct
from typing import List, Optional, Set
from pathlib import Path
from PIL import Image

from pyDXHR.cdcEngine.Archive import ArchivePlatform
from pyDXHR.cdcEngine.DRM.Section import Section
from pyDXHR.cdcEngine.DRM.Resolver import find_resolver, MissingResolver
from pyDXHR.cdcEngine.Sections import AbstractSection
from pyDXHR.cdcEngine.Sections.RenderResource import RenderResource, from_library
from pyDXHR.cdcEngine.DRM.DRMFile import DRM


class Material(AbstractSection):
    def __init__(self, **kwargs):
        self._raw_texture_list = {k: [] for k in range(1, 13)}
        self.TextureLibrary: Optional[str | Path] = kwargs["texture_library"] if "texture_library" in kwargs else None

        self.ImageDict = {}
        self.Diffuse: List[RenderResource | Image] = []
        self.Normal: List[RenderResource | Image] = []
        self.Specular: List[RenderResource | Image] = []
        self.Mask: List[RenderResource | Image] = []
        self.Blend: List[RenderResource | Image] = []
        self.Cubemap: List[RenderResource | Image] = []
        self.Unknown: List[RenderResource | Image] = []

        super().__init__(**kwargs)

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
        pass
        # import pygltflib as gltf
        #
        # if as_library and library_dir:
        #     if not self.TextureLibrary:
        #         raise NotImplementedError
        #     else:
        #         index = 0
        #         gltf_image_list, gltf_texture_list = [], []
        #         for key, value in self.ImageDict.items():
        #             for t_id, image in value:
        #                 gltf_image = gltf.Image()
        #                 gltf_image.name = "T_" + f"{t_id:x}".rjust(8, '0')
        #                 gltf_image.uri = str(image.relative_to(library_dir))
        #                 gltf_image.extras = {
        #                     "cdcTextureId": t_id
        #                 }
        #
        #                 gltf_texture_info = gltf.TextureInfo()
        #                 gltf_texture_info.index = index
        #                 gltf_texture_list.append(gltf_texture_info)
        #
        #                 gltf_image_list.append(gltf_image)
        #
        #     gltf_mat = gltf.Material()
        #     gltf_mat.name = self.Name
        #     gltf_mat.extras = {
        #         "cdcMaterialID": self.ID
        #     }
        #     gltf_mat.emissiveTexture = gltf.TextureInfo(
        #         index=0
        #     )
        #
        #     return gltf_mat, gltf_image_list, gltf_texture_list

    def to_json(self, indent: Optional[int] = 2, use_texture_dict: bool = False):

        if use_texture_dict:
            raise NotImplementedError
            return json.dumps(self.ImageDict, indent=indent)
        else:
            return self._raw_texture_list[3]

    def _get_texture_ids(self):

        for idx in range(1, 13):
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
            _, _, tex_count, _ = struct.unpack_from("4B", self.section.Data, submat_blob_data_offset + 0x14)

            if tex_count:
                for i in range(tex_count):
                    tx_off = texture_data_offset + (16 * i)

                    tex_id, \
                        int1a, int1b1, int1b2, int2, byte1, \
                        tbind, byte3, byte4 = struct.unpack_from(f"{self._endian.value}LHBBLBBBB", self.section.Data,
                                                                 tx_off)

                    self._raw_texture_list[idx].append((tex_id, int1a, int1b1, int1b2, int2, byte1, tbind, byte3, byte4))

    def _deserialize_from_section(self, section):
        super()._deserialize_from_section(section)
        self._get_texture_ids()
        self._get_textures()

    def _get_textures(self):
        # TODO: a biiiiit handwavy, but idc anymore
        seen = []
        submat_3 = self._raw_texture_list[3]
        for tex_id, int1a, int1b1, int1b2, int2, byte1, tbind, byte3, byte4 in submat_3:
            # tex_data = tex_id, int1a, int1b1, int1b2, int2, byte1, tbind, byte3, byte4

            if self.TextureLibrary:
                tex = (tex_id, from_library(tex_id, self.TextureLibrary))
                # tex = tex_data, from_library(tex_id, self.TextureLibrary)
            else:
                tex = tex_id

            if byte1 == 96:
                self.Cubemap.append(tex)
                continue

            if tex_id in seen:
                continue
            else:
                # int1b1, int1b2
                # 0,0
                # 128, 191
                # 0, 191

                if int2 == 4:
                    self.Blend.append(tex)
                    continue
                else:
                    if byte1 == 32:
                        self.Diffuse.append(tex)
                        continue
                    elif byte1 == 128:
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
        }


def guess_materials(int1a, int1b1, int1b2, int2, byte1, tbind, byte3, byte4):    
    # some handwavy bullshit

    if byte1 == 96:
        return "cubemap"

    if int2 == 4:
        return "blend"
    else:
        if byte1 == 32:
            return "diffuse"
        elif byte1 == 128:
            return "normal"


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
