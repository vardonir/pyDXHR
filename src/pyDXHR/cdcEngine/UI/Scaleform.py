from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.Reference import Reference
from pyDXHR.cdcEngine.Sections.RenderResource import RenderResource
from pyDXHR.Export.DDSWriter import OutputFormat
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType, SectionSubtype
from pyDXHR.utils import swf
import numpy as np
from pyDXHR.cdcEngine.Archive import ArchivePlatform, Archive
from pathlib import Path
import struct
from typing import *


# get all SWF:
# {idx: sec for idx, sec in section_list.items() if Path(sec).suffix == ".swf"}


class Scaleform(DRM):
    def __init__(self, **kwargs):
        super().__init__()

        self.cfx: Dict[str, bytes] = {}
        self.textures: Dict[str, RenderResource] = {}

    def dump_cfx(self, dest: str | Path):
        if list(self.cfx.keys())[0] == 1:
            # PC version - no filenames
            pass
        else:
            for key, byte_data in self.cfx.items():
                key = Path(key).relative_to("c:\\dx3")
                dest_path = Path(dest) / key
                dest_path.parent.mkdir(exist_ok=True, parents=True)

                with open(dest_path, "wb") as f:
                    f.write(byte_data)

    def dump_textures(self, dest: str | Path):
        if list(self.textures.keys())[0] == 1:
            pass
        else:
            for key, rr_section in self.textures.items():
                dest_path = Path(dest) / key
                dest_path.parent.mkdir(exist_ok=True, parents=True)
                dest_path = dest_path.with_suffix(".tga")
                rr_section.to_file(OutputFormat.TGA, dest_path)

    def deserialize(self, data: bytes, **kwargs):
        des = super().deserialize(data=data, header_only=False)
        archive: Archive = kwargs.get("arc", None)
        if archive.platform.value in ArchivePlatform.has_complete_file_lists():
            texture_list = archive.texture_list
            section_list = archive.section_list
        else:
            texture_list = None
            section_list = None

        sf_sec = self.lookup_section_subtype(SectionSubtype.Scaleform)
        assert len(sf_sec) == 1
        sf_sec = sf_sec[0]
        sf_ref = Reference.from_drm_section(self, sf_sec)

        root_ref = Reference.from_drm_root(self)

        # l1 = root_ref.access("L")  # 0x1316a
        l1, _, _, _, _, l2 = root_ref.access_array(f"L", 6)
        # l2 = 5

        # dtpid of rr: 1316a
        rr = root_ref.deref(0)

        ll1, _, ll2, ll3 = rr.access_array(f"L", 4)
        # ll1 - not sure
        # ll2, ll3 = seems like a size of some kind

        rr.deref(0x174).deref(0x0).get_string()  # 'scaleform\\OuterShell\\Cursor\\Cursor'
        cfx_count = rr.deref(0xbc).access(f"L")  # int 47

        dtp_id_start = rr.deref(0xac).access(f"L")  # 1316c
        [s for s in self.Sections if s.Header.SecId == rr.deref(0xac).access("L")]

        anim_id = rr.deref(0x3c).access(f"H")  # 1f97
        anim_section = self.lookup_section(SectionType.Animation, anim_id)

        # render model?
        Reference.from_drm_section(self,
                                   [s for s in self.Sections if s.Header.SecId == rr.deref(0xac).access("L")][0]).deref(
            0x68)

        cfx = [
            self.lookup_reference(SectionType.DTPData, 4 + dtp_id_start + i)
            for i in range(1, cfx_count-1)
        ]

        for c in cfx:
            if c:
                byte_data = c.section.Data[4:]
                if section_list:
                    key = section_list[c.section.Header.SecId]
                else:
                    key = c.section.Header.IdHexString

                self.cfx[key] = byte_data

                for res in c.section.Resolvers:
                    if isinstance(c.deref(res.PointerOffset), int):
                        continue

                    sec = c.deref(res.PointerOffset).section
                    if sec.Header.SectionType == SectionType.RenderResource:
                        rr = RenderResource(section=sec)
                        if texture_list:
                            self.textures[texture_list[rr.ID]] = rr
                        else:
                            pass

        # breakpoint()
        #
        # # test = cfx[41] # pc base
        # test = cfx[0] # ps3 base
        #
        # # decompressed = swf.decompress_cfx(test.Data[4:])
        # image_list = swf.export(test.section.Data[4:])
        #
        # if len(image_list) != len(test.section.Resolvers):
        #     breakpoint()
        # if len(image_list) != len([res for res in test.section.Resolvers if test.deref(res.PointerOffset).section.Header.SectionType == SectionType.RenderResource]):
        #     breakpoint()
        #
        # render_resource_list = {}
        #
        # # export render resource sections
        # for (idx, image), res in zip(image_list, test.section.Resolvers):
        #     sec = test.deref(res.PointerOffset).section
        #     if sec.Header.SectionType == SectionType.RenderResource:
        #         rr = RenderResource(section=sec)
        #         render_resource_list[rr.ID] = rr
        #         # rr.to_file(OutputFormat.TGA, save_to=Path(r"F:\Projects\pyDXHR\output\scaleform") / image)
        #
        # breakpoint()
        #
        # u1 = rr.deref(60)
        # u2 = rr.deref(144)
        # u3 = rr.deref(204)
        # u4 = rr.deref(1088)
        #
        # strings = u4.get_string()
        #
        # # from pyDXHR.cdcEngine.DRM.Resolver import LocalDataResolver
        # # aaa = sorted([r for r in rr.section.Resolvers if isinstance(r, LocalDataResolver)], key=lambda x: x.PointerOffset, reverse=True)
        #
        # mtl_and_dtp = [
        #     (
        #         sf_ref.deref(0xa0).deref(0x18 + 0x10 * i),
        #         sf_ref.deref(0xa0).deref(0x1c + 0x10 * i)
        #     )
        #     for i in range(1, 34)
        # ]
        #
        # # script names?
        # [self.lookup_reference(SectionType.Script, i).deref(0x10).get_string() for i in range(0x1313D, 0x1316F) if
        #  self.lookup_reference(SectionType.Script, i) is not None and self.lookup_reference(SectionType.Script,
        #                                                                                     i).deref(0x10) is not None]
        #
        # # debug menu?
        # cfx1_len = sf_ref.deref(0x94).access("L")
        # cfx_data = sf_ref.deref(0x94).section.Data[4:cfx1_len+4]
        # textures = [sf_ref.deref(0x94).deref(0xda80 + (0x104*i)) for i in range(29)]
        #
        # cfx = [self.lookup_section(SectionType.DTPData, i) for i in range(0x13170, 0x1319f)]
        #
        # sf_ref.deref(0x120) # 77725
        #
        # # sf_ref.section.Data[sf_ref.deref(0x6c).offset:]  # 77725
        # sf_ref.deref(0x6c).access("L") # 77725
        # sf_ref.deref(0x6c).access_array("H", 4) # (12189, 1, 1, 0)
        #
        # sf_ref.deref(0xd8).get_string()  # '_root.mainLoading_mc'
        # sf_ref.deref(0xdc).get_string()  # Loading_
        #
        # sf_ref.deref(0x74).access_array("H", 8)  # (0, 0, 12619, 1)
        #
        # sf_ref.deref(0x7c).access_array("H", 4)  # (12189, 1, 1, 0)
        # sf_ref.deref(0x7c).access_array("L", 4)
        # sf_ref.deref(0x88).access("L")
        # # (12189, 1, 1, 0)
        #
        # # ???
        # sf_ref.deref(0x12c).access("L")
        #
        # sf_ref.deref(0x9c).get_string()
        # sf_ref.deref(0xb0).get_string()
        #
        # breakpoint()



if __name__ == "__main__":
    from pyDXHR.cdcEngine.Archive import Archive
    arc = Archive()
    # arc.deserialize_from_env()
    arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHRPS3\CACHE.000")

    db = arc.get_from_filename("globalscaleformdatabase.drm")
    drm = Scaleform()
    drm.deserialize(db, arc=arc)

    drm.dump_cfx(r"F:\Projects\pyDXHR\output\ps3_scaleform")
    drm.dump_textures(r"F:\Projects\pyDXHR\output\ps3_scaleform")
