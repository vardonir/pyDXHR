from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.MasterunitDRM import MasterunitDRM

pc_arc = Archive()
pc_arc.deserialize_from_env()

file = "det_city"
# det_sarifhq__masterunit

pc_drm = MasterunitDRM(
    masterunit_name=file,
    archive=pc_arc,
    obj=False,
    skip_ext_imf=True
)

# pc_drm.to_gltf(save_to=fr"C:\Users\vardo\DXHR_Research\pyDXHR_public\output\masterunit_gltf\{file}",
#                apply_universal_scale=False,
#                blank_materials=True)
