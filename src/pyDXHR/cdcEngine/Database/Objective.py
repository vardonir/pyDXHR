from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.Section import Section
from pyDXHR.cdcEngine.DRM.Reference import Reference
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
from pyDXHR.cdcEngine.Locals import Locals
from pyDXHR.cdcEngine.Archive import ArchiveEntry
from typing import Optional, Dict


class ObjectiveDatabase(DRM):
    def __init__(self, **kwargs):
        super().__init__()

    def deserialize(self, data: bytes, **kwargs):
        import numpy as np

        des = super().deserialize(data=data, header_only=False)
        if not des:
            breakpoint()

        archive = kwargs.get("arc", None)

        if archive:
            locals_bin = Locals.from_archive(archive)
        else:
            locals_bin = None

        root_ref = Reference.from_drm_root(self)
        header = np.frombuffer(root_ref.section.Data, dtype=np.dtype(np.uint32).newbyteorder(self.Header.Endian.value))
        len_texts = header[0]
        text_ids = header[1:]
        assert len_texts == text_ids.size

        text_refs = [
            self.lookup_reference(SectionType.DTPData, s_id)
            for s_id in text_ids
        ]

        for ref in text_refs:
            u1, u2 = ref.access_array("H", 2)
            u3, mission_id, u5, u6 = ref.access_array("I", 4, offset=4)

            ref2 = self.lookup_reference(SectionType.DTPData, mission_id)
            ref2_1, ref2_2 = ref2.access_array("H", 2)
            if locals_bin:
                task_title = locals_bin.get_string(u1)
                task_desc = locals_bin.get_string(u2)
                mission_title = locals_bin.get_string(ref2_1)
                mission_desc = locals_bin.get_string(ref2_2)

        # TODO: - move to separate class
        #       - mod stuff


if __name__ == "__main__":
    from pyDXHR.cdcEngine.Archive import Archive
    arc = Archive()
    # arc.deserialize_from_env()
    # arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHR 1.0.499.0 beta\BIGFILE.000")
    # arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHRPS3\CACHE.000")
    arc.deserialize_from_file(r"F:\Games\Deus Ex HRDC\BIGFILE.000")

    db = arc.get_from_filename("objective_database.drm")
    drm = ObjectiveDatabase()
    drm.deserialize(db, arc=arc, localization=0xFFFFFD61)

    breakpoint()
