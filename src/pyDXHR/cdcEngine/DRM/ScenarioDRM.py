from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM
from pyDXHR.cdcEngine.DRM.Reference import Reference


class ScenarioDRM(UnitDRM):
    def __init__(self):
        super().__init__()

    def deserialize(self, data: bytes, **kwargs):
        super().deserialize(db, **kwargs)

        root_ref = Reference.from_drm_root(self)
        breakpoint()


if __name__ == "__main__":
    from pyDXHR.cdcEngine.Archive import Archive

    arc = Archive()
    # arc.deserialize_from_env()
    arc.deserialize_from_file(r"F:\Games\Deus Ex HRDC\BIGFILE.000")

    # literally one static computer in this file -
    # dtp_id of the username/pw combo is 63309 (hrdc)
    db = arc.get_from_filename("s_scn_det_sarif_industries_sarifcomputerinteractive_det_sarif_industries.drm")
    drm = ScenarioDRM()
    drm.deserialize(db, archive=arc)

    breakpoint()