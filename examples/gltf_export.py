from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM import DRM
from pyDXHR.export import gltf

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PS3)
bf.open()

imf = "imf\imf_props\imf_vehicule\chopper_int\chopper_int.drm"  # noqa
obj = "television_extralarge.drm"

drm = DRM.from_bigfile(obj, bf)
drm.open()

gltf.from_drm(drm,
              save_to=rf"C:\Users\vardo\Documents\pyDXHR\playground\test.gltf",
              scale=0.002, z_up=True
              )

breakpoint()
