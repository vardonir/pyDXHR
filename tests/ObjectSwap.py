from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.Mods import UnitMod

# pick a unit where you want to swap stuff in
file = "det_sarif_industries.drm"

# load the data
arc = Archive()
arc.deserialize_from_env()
data = arc.get_from_filename(file)

# read it as a DRM
drm = DRM()

# to optimize, skip everything but the objects
drm.deserialize(data)

# for example, I want to replace all ebooks in the sarif HQ with praxis kits
new_data = UnitMod.replace_object(old_obj_id=136, new_obj_id=223, drm=drm, byte_data=data)
# 136,ebook_a
# 223,praxiskit

from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM

unit = UnitDRM()
unit.deserialize_from_decompressed(
    new_data,
    archive=arc,
    imf=False,
    stream=False,
    obj=True,
    occlusion=False,
    cell=False,
    collision=False,
)

breakpoint()

# imf\imf_props\imf_supplies\imf_food\box_cereal_a\box_cereal_a.drm

