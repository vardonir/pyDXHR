from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pathlib import Path

arc = Archive()
arc.deserialize_from_env()

# arc = Archive()
# arc.deserialize_from_file(r"F:\DXHRDCWII\bigfile-wiiu.000")

# arc = Archive()
# arc.deserialize_from_file(r"F:\DXHRPS3\CACHE.000")

data = arc.get_from_filename("det_city_sarif.drm")
drm = UnitDRM(
    uniform_scale=0.002,
    z_up=True
)

drm.deserialize(data,
                imf=False,
                obj=True,
                stream=False,
                occlusion=False,
                cell=False
                )

# for idx, cm in enumerate(drm.CollisionMesh):
#     cm.to_gltf(save_to=fr"F:\pyDXHR\output\collision\{idx}.gltf")
