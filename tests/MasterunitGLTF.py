from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.MasterunitDRM import MasterunitDRM

pc_arc = Archive()
pc_arc.deserialize_from_env()

file = "det_city"
# file = "det_sarifhq"
# det_sarifhq__masterunit

pc_drm = MasterunitDRM(
    masterunit_name=file,
    archive=pc_arc,
    # limit_units=3,

    uniform_scale=0.002,
    z_up=True,
    split_by_occlusion=True,

    # imf=False,
    # skip_int_imf=True,
    # stream=False,
    # obj=False,
    # occlusion=False,
    # cell=False,
    # collision=True,
)

pc_drm.to_gltf(
    save_to=fr"F:\Projects\pyDXHR\output\masterunit_gltf\{file}",
    # skip_materials=True,
    merge=False
)
