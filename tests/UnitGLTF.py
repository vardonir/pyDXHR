from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM

arc = Archive()
arc.deserialize_from_env()
# arc.deserialize_from_file(r"F:\Game_Rips\deus-ex-human-revolution\raw\archive\PC_DC\BIGFILE.000")

# one_track_mind = "det_city_sarif.drm"  # the one that matters
# hehe_its_a_track_get_it = "det_city_tunnel1.drm"  # it's a track
# just_a_dipshit_from_detroit = "det_adam_apt_c.drm"  # a lot of everything, but is kinda big
# im_a_fucking_corpo_shill = "det_sarif_industries.drm"  # the one that really matters, but you keep stalling it
file = "det_city_sarif.drm"
pc_data = arc.get_from_filename(file)


# read as unit
pc_drm = UnitDRM(
    uniform_scale=0.002,
    z_up=True
)
pc_drm.deserialize(
    pc_data,
    archive=arc,
    split_objects=True,

    # imf=False,
    # stream=False,
    obj=False,
    # occlusion=True,
    # cell=False,
    # collision=False,
)

pc_drm.to_gltf(
    save_to=fr"F:\pyDXHR\unit_gltf\{file}",
    skip_materials=True,
    # blank_materials=False
)

# TODO: either attach the fixed materials (ie, figure out the method),
#  or set it to blank materials, import the gltf as a datasmith, and then
#  fix the materials using a python script in ue
