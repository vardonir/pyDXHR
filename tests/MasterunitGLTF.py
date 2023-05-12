from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.MasterunitDRM import MasterunitDRM

pc_arc = Archive()
pc_arc.deserialize_from_env()

file = "det_city"
# det_sarifhq__masterunit

pc_drm = MasterunitDRM(
    masterunit_name=file,
    archive=pc_arc,

    uniform_scale=0.002,
    z_up=True,

    imf=False,
    # skip_int_imf=True,
    stream=False,
    obj=False,
    occlusion=True,
    cell=False,
    collision=False,
)

# TODO:
#       - run the finish the masterunit merge code

pc_drm.to_gltf(save_to=fr"F:\pyDXHR\masterunit\{file}",
               blank_materials=True,
               merge=True
               )

breakpoint()
