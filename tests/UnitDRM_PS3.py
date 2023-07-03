from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM

arc = Archive()
arc.deserialize_from_env("PS3_DC")

file = "det_city_sarif.drm"
data = arc.get_from_filename(file)

# read as unit
drm = DRM()
des = drm.deserialize(data)

breakpoint()