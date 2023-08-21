from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM import DRM
from pyDXHR.export import gltf

# Assumes that you have the PC Director's Cut edition specified in env
bf = Bigfile.from_env()
# bf.unpack_from = 'cache'
bf.open()

imf = "imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_sarif_office\sarif_office_fire_a\sarif_office_fire_a.drm"  # noqa
obj = "car_2027_a.drm"

drm = DRM.from_bigfile(obj, bf)
drm.open()

gltf.from_drm(drm, save_to=r"C:\Users\vardo\Documents\pyDXHR\playground\mesh\obj_lumen.glb")
# breakpoint()
