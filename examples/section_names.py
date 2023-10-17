from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM import DRM

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PS3)
bf.open()

# drm = "det_sarif_industries.drm"
# drm = r"imf\imf_props\imf_vehicule\chopper_int\chopper_int.drm"
drm = "television_extralarge.drm"

drm = DRM.from_bigfile(drm, bf)
drm.open()
drm.parse_filenames(bf)

breakpoint()
