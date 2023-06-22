"""
Partially based on https://github.com/rrika/dxhr/blob/main/tools/dump_scenarios.py
"""

from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.Reference import Reference
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
import numpy as np
import struct


class ScenarioDatabase(DRM):
    def __init__(self, **kwargs):
        super().__init__()

    def deserialize(self, data: bytes, **kwargs):
        des = super().deserialize(data=data, header_only=False)

        root_ref = Reference.from_drm_root(self)
        header = np.frombuffer(root_ref.section.Data, dtype=np.uint32)
        len_scenes = header[0]
        scene_ids = header[1:]
        assert scene_ids.size == len_scenes

        scene_refs = [
            self.lookup_reference(SectionType.DTPData, s_id)
            for s_id in scene_ids
        ]

        scenes = {}
        for ref in scene_refs:
            script_id, count = ref.access_array("L", 2)
            script_ref = self.lookup_reference(SectionType.Script, script_id)

            if ref.deref(0x14):
                scene_name = ref.deref(0x14).get_string()
            else:
                scene_name = None

            scenes[ref.section.Header.SecId] = scene_name
            # for i in range(count):
            #     breakpoint()

        # for scn_id in scn_ids:
        #     # r = drm.Reference(scndb, db.index[7, scn_id][2])
        #     r = db.lookup(7, scn_id)
        #     script_id = r.access(uint32, 0)[0]
        #     count_a = r.access(uint32, 4)[0]
        #     entries_a = r.deref(8)
        #     count_b = r.access(uint32, 12)[0]
        #
        #     lines = []
        #
        #     for ia in range(count_a):
        #         entry_a = entries_a.add(ia * 8)
        #         name = entry_a.deref(0)
        #         num4 = entry_a.access(uint16, 4)[0]
        #         num6 = entry_a.access(uint16, 6)[0]
        #         name = name.access_null_terminated().decode("ascii") if name else "(unnamed)"
        #         lines.append("{:04x} {:04x} {}".format(num4, num6, name))
        #     yield scn_id, count_a, count_b, lines

        breakpoint()


if __name__ == "__main__":
    from pyDXHR.cdcEngine.Archive import Archive
    arc = Archive()
    arc.deserialize_from_env()

    db = arc.get_from_filename("scenario_database.drm")
    drm = ScenarioDatabase()
    drm.deserialize(db)
