from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM import DRM
from pyDXHR.export import gltf

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
bf.open()

imf = "imf\imf_props\imf_vehicule\chopper_int\chopper_int.drm"  # noqa
obj = "television_extralarge.drm"
char = "civilian_davidsarif.drm"

drm = DRM.from_bigfile(char, bf)
drm.open()

try:
    drm.parse_filenames(bf)
except FileNotFoundError:
    pass

gltf.from_drm(drm,
              save_to=rf"C:\Users\vardo\Documents\pyDXHR\playground\civilian_davidsarif_2.gltf",
              scale=0.002, z_up=True
              )

# breakpoint()
