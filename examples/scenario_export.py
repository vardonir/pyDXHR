""" A mildly-stupid method for exporting all scenarios associated with a unit """

from pathlib import Path
from pyDXHR.Bigfile import Bigfile, filelist
from pyDXHR.DRM.unit import UnitDRM
from pyDXHR.export import unit

bf = Bigfile.from_env()
bf.open()

unit_key = "det_city_police"
save_to = rf"C:\Users\vardo\Documents\pyDXHR\playground\unit\{unit_key}"
Path(save_to).mkdir(parents=True, exist_ok=True)

fl = filelist.read_filelist("pc-w")
scn_list = []

for _, path in fl.items():
    if unit_key in path and path.startswith("s_scn"):
        if "global" in path: continue
        if "lbw" in path: continue
        if "sce" in path: continue

        scn_list.append(path)

for scn in scn_list:
    drm = UnitDRM.from_bigfile(scn, bf)
    drm.open()

    unit.from_drm(
        drm, bf,
        save_to=save_to + "/unit_drm",
        scale=0.002, z_up=True,
        # stream=False,
        # cell=False,
        # int_imf=False,
        # ext_imf=False,
        # obj=False,
    )

breakpoint()
