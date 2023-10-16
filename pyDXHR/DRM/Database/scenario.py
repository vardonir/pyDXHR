from pyDXHR.DRM.resolver import Reference
from pyDXHR import SectionType


class ScenarioDatabase:
    def __init__(self):
        self.drm = None
        self.scene_names = {}
        self._is_open = False

    @classmethod
    def from_bigfile(cls, bf):
        from pyDXHR.DRM import DRM

        obj = cls()
        obj.drm = DRM.from_bigfile("scenario_database.drm", bf)
        obj.drm.open()
        return obj

    def open(self):
        from pyDXHR.DRM.utils import get_text_references

        self._is_open = True
        scene_references = get_text_references(self.drm)

        self.scene_names = {}
        for ref in scene_references:
            script_id, count_a, _, count_b = ref.access("4L")
            script_ref = Reference.from_section_type(
                self.drm, section_type=SectionType.script, section_id=script_id
            )

            if ref.deref(0x14):
                scene_name = ref.deref(0x14).access_string().lower()
            else:
                continue

            self.scene_names[ref.section.header.section_id] = scene_name
            # if ref.section.Header.SecId == 1586:  # 's_scn_det01_sq02_cassandra_end_det_adam_apt_a'
            #     # E11C7 <- one of the lines from the conversation
            #     # 8.730 - E10DB <- this code shows up at this offset
            #
            #     scn_dat = self.bigfile.get_from_filename(scene_name + ".drm")
            #     if scn_dat is None:
            #         continue
            #
            #     drm = DRM.from_bigfile(scn_dat, self.bigfile)
            # scn_root_ref = Reference.from_drm_root(scn)
            #
            # ref20 = scn.lookup_reference(SectionType.Script, script_ref.deref(0x14).deref(0x20).access("L"))
            # ref48 = scn.lookup_reference(SectionType.Script, script_ref.deref(0x14).deref(0x48).access("L"))
            # breakpoint()

        # breakpoint()
