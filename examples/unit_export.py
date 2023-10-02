from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM.unit import UnitDRM
from pyDXHR.export import unit

bf = Bigfile.from_env()
bf.open()

unit_drm = "det_sarifhq_rail_tutorial.drm"
# unit_drm = "s_scn_det1_city_sarif_det_city_sarif.drm"

drm = UnitDRM.from_bigfile(unit_drm, bf)
drm.open()

unit.from_drm(
    drm, bf,
    save_to=rf"C:\Users\vardo\Documents\pyDXHR\playground\unit\{unit_drm}",
    scale=0.002, z_up=True,
    # stream=False,
    # cell=False,
    # int_imf=False,
    # ext_imf=False,
    # obj=False,
    generate_library=True
)

# breakpoint()
