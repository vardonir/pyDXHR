from pathlib import Path
import kaitaistruct
from typing import Optional, Set

from pyDXHR.cdcEngine.Archive import ArchivePlatform
from pyDXHR.cdcEngine.DRM.Section import Section
from pyDXHR.cdcEngine.Sections import AbstractSection
from pyDXHR.KaitaiGenerated.PCD import Pcd as PCDImageFormat
from pyDXHR.KaitaiGenerated.PS3T import Ps3t as PS3TImageFormat
from pyDXHR.Export.DDSWriter import DDSImage, OutputFormat
from pyDXHR.cdcEngine.DRM.DRMFile import DRM


class RenderResource(AbstractSection):
    def __init__(self, **kwargs):
        self.ResourceType: Optional[type] = None
        self.Payload = None

        self.Height: int = 0
        self.Width: int = 0
        self.Format = None
        self.LenMipMaps: int = 0

        self.Image: Optional[DDSImage] = None
        super().__init__(**kwargs)

    def _deserialize_from_section(self, sec: Section):
        super()._deserialize_from_section(sec)
        try:
            image_data = PCDImageFormat.from_bytes(sec.Data)
        except kaitaistruct.ValidationNotEqualError:
            try:
                image_data = PS3TImageFormat.from_bytes(sec.Data)
            except kaitaistruct.ValidationNotEqualError:
                raise NotImplementedError
            else:
                self.ResourceType = PS3TImageFormat
                self.LenMipMaps = 0
                self.Format = image_data.format
        else:
            self.ResourceType = PCDImageFormat
            self.LenMipMaps = image_data.len_mipmaps
            self.Format = image_data.format.value

        self.Height, self.Width = image_data.height, image_data.width
        self.Payload = image_data.payload

        self.Image = DDSImage(
            height=self.Height,
            width=self.Width,
            texture_format=self.Format,
            payload=self.Payload,
            len_mipmaps=self.LenMipMaps
        )

    @staticmethod
    def _get_name_from_archive(archive, sec_id):
        if archive is not None and archive.platform.value in ArchivePlatform.has_complete_file_lists():
            return archive.texture_list[sec_id]
        else:
            return "RenderResource_" + f"{sec_id:x}".rjust(8, '0')

    def to_gltf(self, use_dds: bool = False, as_blob: bool = False):
        pass
        # import pygltflib as gltf
        # if use_dds:
        #     gltf_image = gltf.Image(
        #
        #     )

    def to_file(self, image_format: OutputFormat, save_to: Path | str):
        self.Image.save_as(image_format=image_format, save_to=save_to)


def deserialize_drm(
        drm: DRM
) -> Set[RenderResource]:
    from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
    return {RenderResource(section=s) for s in drm.Sections if s.Header.SectionType == SectionType.RenderResource}


def from_library(tex_id: int, tex_lib_dir: str | Path, as_path: bool = True):
    from glob import glob
    from PIL import Image

    file = glob(str(Path(tex_lib_dir) / f"{tex_id:x}".rjust(8, '0')) + ".*")
    if len(file) > 1:
        raise Exception
    elif len(file) == 0:
        raise Exception
    else:
        file = file[0]
        if as_path:
            return Path(file)
        else:
            return Image.open(file)


def from_named_textures(tex_id: int, named_tex_dir: str | Path, get_name_only: bool = False):
    with open(named_tex_dir, "r") as file:
        for ln in file:
            t_id, name = ln.strip().split(",")
            if int(t_id) == tex_id:
                break
        else:
            # not found in file
            return None

    if "_" not in name:
        if "flat" in name:
            return "flat" if not get_name_only else name
        if "dummy" in name:
            return "flat" if not get_name_only else name
        if "light" in name:
            return "light" if not get_name_only else name
        else:
            return "unknown" if not get_name_only else name
    if "cube" in name:
        return "cubemap"

    found_name = name.split("_")

    if "diffuse" in name:
        return "diffuse" if not get_name_only else name
    if "normal" in name:
        return "normal" if not get_name_only else name
    if "specula" in name: # there's one there called "speculaire"...
        return "specular" if not get_name_only else name
    if "blend" in name:
        return "blend" if not get_name_only else name
    if "mask" in name:
        return "mask" if not get_name_only else name

    if found_name[-1] == "d":
        return "diffuse" if not get_name_only else name
    if found_name[-1] == "n":
        return "normal" if not get_name_only else name
    if found_name[-1] == "m":
        return "mask" if not get_name_only else name
    if found_name[-1] == "s":
        return "specular" if not get_name_only else name
    # if found_name[-1] == "b":
        # this could really be anything, not necessarily "blend"
        # pass

    return "unknown" if not get_name_only else name


if __name__ == "__main__":
    from pyDXHR.cdcEngine.Archive import Archive
    from pyDXHR.cdcEngine.DRM.DRMFile import DRM
    from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType

    pc_base = r"C:\Users\vardo\DXHR_Research\DXHR\BIGFILE.000"
    pc_dc = r'C:\Program Files (x86)\GOG Galaxy\Games\Deus Ex HRDC\BIGFILE.000'
    ps3_cache = r"C:\Users\vardo\DXHR_Research\DXHRDCPS3\CACHE.000"

    pc_arc = Archive()
    pc_arc.deserialize_from_file(pc_base)

    ps3_arc = Archive()
    ps3_arc.deserialize_from_file(ps3_cache)

    dxt1_example = r"art\texture_library\cube_map\cubemap_sarifhq_atrium_a.drm"
    a8r8g8b8_example = r"object\lighting\lightbeams\textures\lightbeamb.drm"

    ps3t_example = r"art\texture_library\cube_map\adam_cubemap_a_diffuse.drm"

    pc_data = pc_arc.get_from_filename(a8r8g8b8_example)

    ps3_data = ps3_arc.get_from_filename(ps3t_example)

    pc_drm = DRM()
    pc_drm.deserialize(pc_data)

    ps3_drm = DRM()
    ps3_drm.deserialize(ps3_data)

    tex_sec = pc_drm.filter_by_type([SectionType.RenderResource])[0]
    ps3_tex_sec = ps3_drm.filter_by_type([SectionType.RenderResource])[0]

    pc_rm = RenderResource(section=tex_sec)
    ps3_rm = RenderResource(section=ps3_tex_sec)

    pc_rm.to_file(OutputFormat.TGA, save_to=r"C:\Users\vardo\DXHR_Research\pyDXHR\preprocessed\new_texture_converter\a8r8g8b8.tga")
    ps3_rm.to_file(OutputFormat.TGA, save_to=r"C:\Users\vardo\DXHR_Research\pyDXHR\preprocessed\new_texture_converter\ps3.tga")
    # breakpoint()
