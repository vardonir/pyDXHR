from pathlib import Path
import struct

from pyDXHR.DRM.Section import RenderResource
from pyDXHR.DRM.resolver import Reference, Resolver
from pyDXHR import SectionType


class GlobalScaleformDatabase:
    def __init__(self):
        self._is_open = False
        self.drm = None
        self.cfx_dict = {}
        self.texture_dict = {}
        self.cfx_texture_map = {}

    def dump_to_folder(self, folder_path: Path | str):
        for sec_id, cfx_data in self.cfx_dict.items():
            cfx_path = Path(folder_path) / f"{sec_id:08X}.cfx"
            with open(cfx_path, "wb") as f:
                f.write(cfx_data)

        for sec_id, rr in self.texture_dict.items():
            tex = rr.read()
            tex.to_png(folder_path)

    @classmethod
    def from_bigfile(cls, bf):
        from pyDXHR.DRM import DRM

        obj = cls()
        obj.drm = DRM.from_bigfile("globalscaleformdatabase.drm", bf)
        obj.drm.open()
        return obj

    def open(self):
        self._is_open = True
        root_ref = Reference.from_root(self.drm)

        ref_sub0 = root_ref.deref(0)
        cfx_count = ref_sub0.deref(0xBC).access(f"L")
        dtp_id_start = ref_sub0.deref(0xAC).access(f"L")

        cfx_refs = [
            Reference.from_section_type(
                drm_or_section_list=self.drm,
                section_type=SectionType.dtpdata,
                section_id=4 + dtp_id_start + i,
            )
            for i in range(1, cfx_count - 1)
        ]

        for cfx in cfx_refs:
            if cfx:
                (cfx_length,) = struct.unpack(
                    f"{self.drm.endian}L", cfx.section.data[0:4]
                )
                byte_data = cfx.section.data[4:]
                sec_id = cfx.section.header.section_id

                self.cfx_dict[sec_id] = byte_data
                self.cfx_texture_map[sec_id] = []

                # a bit brute-force-y, but whatever
                res: Resolver
                for res in cfx.section.resolvers:
                    if res.missing_resolver is not None:
                        continue

                    res_sec = cfx.deref(res.pointer_offset).section
                    if res_sec.header.section_type == SectionType.render_resource:
                        rr = RenderResource.from_section(res_sec)
                        self.texture_dict[rr.section_id] = rr
                        self.cfx_texture_map[sec_id].append(rr.section_id)
