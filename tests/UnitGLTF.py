from tqdm import tqdm
from pathlib import Path
from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM

arc = Archive()
# arc.deserialize_from_env("PS3_DC")
arc.deserialize_from_env()

# some unit notes:
#       det_city_tunnel1 - has everything except internal RM
#       det_sarif_industries - large but mos\tly self-contained, no internal RT
#       det_adam_apt_c - the apartment itself is one big external RT. the background mesh is massive
#       det_city_sarif - no internal RT. raises an error on the ps3 version

# one_track_mind = "det_city_sarif.drm"  # the one that matters
# hehe_its_a_track_get_it = "det_city_tunnel1.drm"  # it's a track - useful small unit for testing
# just_a_dipshit_from_detroit = "det_adam_apt_c.drm"  # a lot of everything, but is kinda big
# im_a_fucking_corpo_shill = "det_sarif_industries.drm"  # the one that really matters, but you keep stalling it

file = "det_city_sarif.drm"
pc_data = arc.get_from_filename(file)

# read as unit
drm = UnitDRM(
    uniform_scale=0.002,
    z_up=True,
)
drm.deserialize(
    pc_data,
    archive=arc,
    split_by_occlusion=True,

    # # imf=False,
    # # skip_ext_imf=True,
    # skip_int_imf=True,
    # stream=False,
    obj=False,
    occlusion=False,
    # # cell=False,
    collision=True,
)

drm.to_gltf(
    save_to=fr"F:\Projects\pyDXHR\output\unit_gltf\{file}",
    skip_materials=True
)

# pc_drm.to_gltf(
#     save_to=fr"C:\Users\vardo\Nextcloud\pyDXHR\{file}",
# )

# breakpoint()