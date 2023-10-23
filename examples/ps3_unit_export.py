from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM.unit import UnitDRM
from pyDXHR.export import unit

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PS3)
bf.open()

unit_drm = "det_city_sarif.drm"

drm = UnitDRM.from_bigfile(unit_drm, bf)
drm.open()
drm.parse_filenames(bf)

unit.from_drm(
    drm, bf,
    save_to=rf"C:\Users\vardo\Documents\pyDXHR\playground\ps3\{unit_drm}",
    scale=0.002, z_up=True,
    stream=False,
    cell=False,
    # int_imf=False,
    ext_imf=False,
    obj=False,
)

breakpoint()
