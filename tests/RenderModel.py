from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.Sections import RenderMesh

models = [
    # has transparency
    r"imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_atrium\fake_floor30_a\fake_floor30_a.drm",

    #
    r"imf\imf_architecture\imf_buildings\imf_detroit\imf_background\det_bgd_building_gm_a\det_bgd_building_gm_a.drm",

    #
    r"imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_lab_modules\det_sarifhq_door_static_a\det_sarifhq_door_static_a.drm"
]

arc = Archive()
arc.deserialize_from_env()

data = arc.get_from_filename(models[0])

assert data[0:4] == b'CDRM'

drm = DRM()
stat = drm.deserialize(data)
assert stat

rm_sec_set = RenderMesh.deserialize_drm(drm)

breakpoint()
