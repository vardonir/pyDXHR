from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pathlib import Path

arc = Archive()
arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHRDCWII\bigfile-wiiu.000")
# arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHRDCPS3\CACHE.000")

pc_arc = Archive()
pc_arc.deserialize_from_env()

fn = "det_city_sarif.drm"

def get_drm(arc, fn):
    data = arc.get_from_filename(fn)
    drm = UnitDRM()
    drm.deserialize(data,
                    archive=arc,
                    cell=False)
    return drm

for_exam = get_drm(arc, fn)
# pc_base = get_drm(pc_arc, fn)

breakpoint()
# for idx, cm in enumerate(drm.CollisionMesh):
#     cm.to_gltf(save_to=fr"F:\pyDXHR\output\collision\{idx}.gltf")
