from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM.unit import UnitDRM
from pyDXHR.export import unit

# Assumes that you have the PC Director's Cut edition specified in env
bf = Bigfile.from_env()
# bf.unpack_from = 'cache'
bf.open()

# unit_drm = "det_city_tunnel1.drm"
unit_drm = "s_scn_det1_city_sarif_det_city_sarif.drm"

drm = UnitDRM.from_bigfile(unit_drm, bf)
# drm.open()

unit.from_drm(drm, bf, save_to=r"C:\Users\vardo\Documents\pyDXHR\playground\unit")
breakpoint()
