from tqdm import tqdm
from pathlib import Path
from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM

arc = Archive()
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

# with "det_city_sarif.drm" as file:
for file in [Path(u).stem + ".drm" for u in arc.unit_list]:
    if "det" not in file:
        continue
    if "fema" in file:
        continue

    pc_data = arc.get_from_filename(file)
    if pc_data:

        drm = UnitDRM(
            uniform_scale=0.002,
            z_up=True,
        )
        drm.deserialize(
            pc_data,
            archive=arc,
            # split_by_occlusion=True,

            # # imf=False,
            # # skip_ext_imf=True,
            # skip_int_imf=True,
            # stream=False,
            # # obj=False,
            # # occlusion=False,
            # # cell=False,
            # collision=False,
        )

        drm.to_gltf(
            save_to=fr"D:\UE5\ProjectSIX\Raw\unit\{file}",
            # skip_materials=True
        )

# breakpoint()