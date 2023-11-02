from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM.Section import CollisionMesh

bf = Bigfile.from_env()
bf.open()

unit_drm = "det_sarifhq_rail_tutorial.drm"

from pyDXHR.DRM import DRM
drm = DRM.from_bigfile(unit_drm, bf)
drm.open()

coll_mesh = CollisionMesh.from_drm(drm)
for c in coll_mesh:
    md = c.read()
    md.to_gltf(fr"C:\Users\vardo\Documents\pyDXHR\playground\collmesh\{unit_drm}_coll.gltf")

breakpoint()
