from tqdm import tqdm
from pathlib import Path
from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM

arc = Archive()
arc.deserialize_from_env()
# arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHR 1.0.499.0 beta\BIGFILE.000")
# arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHRPS3\CACHE.000")
# arc.deserialize_from_file(r"F:\Games\Deus Ex HRDC\BIGFILE.000")

# one_track_mind = "det_city_sarif.drm"  # the one that matters
# hehe_its_a_track_get_it = "det_city_tunnel1.drm"  # it's a track - useful small unit for testing
# just_a_dipshit_from_detroit = "det_adam_apt_c.drm"  # a lot of everything, but is kinda big
# im_a_fucking_corpo_shill = "det_sarif_industries.drm"  # the one that really matters, but you keep stalling it

file = "det_sarif_industries.drm"
pc_data = arc.get_from_filename(file)


# read as unit
pc_drm = UnitDRM(
    uniform_scale=0.002,
    z_up=True
)
pc_drm.deserialize(
    pc_data,
    archive=arc,
    # split_by_occlusion=True,

    # imf=False,
    # skip_ext_imf=True,
    # stream=False,
    # obj=False,
    # occlusion=False,
    # cell=False,
    # collision=True,
)

# pc_drm.to_gltf(
    # save_to=fr"F:\Projects\pyDXHR\output\unit_gltf\{file}",
# )

pc_drm.to_gltf(
    save_to=fr"C:\Users\vardo\Nextcloud\pyDXHR\{file}",
)

# breakpoint()