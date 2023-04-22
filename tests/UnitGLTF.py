from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM

pc_arc = Archive()
pc_arc.deserialize_from_env()

# one_track_mind = "det_city_sarif.drm"  # the one that matters
# hehe_its_a_track_get_it = "det_city_tunnel1.drm"  # no internal IMFs, but has stream objects
# just_a_dipshit_from_detroit = "det_adam_apt_c.drm"  # a lot of everything, but is kinda big
# im_a_fucking_corpo_shill = "det_sarif_industries.drm"  # the one that really matters, but you keep stalling it
file = "det_city_tunnel1.drm"
pc_data = pc_arc.get_from_filename(file)

# read as unit
pc_drm = UnitDRM(
    uniform_scale=0.002,
    z_up=True
)
pc_drm.deserialize(
    pc_data,
    archive=pc_arc,
    split_objects=True,
    # imf=True,
    # stream=False,
    # obj=False,
    # skip_ext_imf=False,
)
# pc_drm.deserialize(pc_data)  # not attaching the archive just spits out the internal IMFs

pc_drm.to_gltf(save_to=fr"C:\Users\vardo\DXHR_Research\pyDXHR_public\output\unit_gltf\{file}",
               blank_materials=True)

# pc_drm.to_ue5_csv(
#     save_to=fr"C:\Users\vardo\DXHR_Research\pyDXHR_public\output\unit_ue5\{file}",
# )
