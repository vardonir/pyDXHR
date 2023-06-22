from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.Reference import Reference
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType, SectionSubtype
import numpy as np
import struct


class Loading(DRM):
    def __init__(self, **kwargs):
        super().__init__()

    def deserialize(self, data: bytes, **kwargs):
        des = super().deserialize(data=data, header_only=False)

        # sf_sec = self.lookup_section_subtype(SectionSubtype.Scaleform)
        # assert len(sf_sec) == 1
        # sf_sec = sf_sec[0]

        root_ref = Reference.from_drm_root(self)

        rr = root_ref.deref(0)

        u1 = rr.deref(60)
        u2 = rr.deref(144)
        u3 = rr.deref(204)
        u4 = rr.deref(1088)

        strings = [rr.deref(676).deref(16 + i*20).get_string() for i in range(17)]

        # render model
        rr.deref(0x150).deref(0x64)

        # floats?
        rr.deref(0x150).deref(0xc).access_array("f", 9)

        breakpoint()



if __name__ == "__main__":
    from pyDXHR.cdcEngine.Archive import Archive
    arc = Archive()
    arc.deserialize_from_env()

    db = arc.get_from_filename("globalloading.drm")
    drm = Loading()
    drm.deserialize(db)
