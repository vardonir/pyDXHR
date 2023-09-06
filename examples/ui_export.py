from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM.Specific.globalscaleformdatabase import GlobalScaleformDatabase

bf = Bigfile.from_env()
bf.open()

global_scaleform_db = GlobalScaleformDatabase.from_bigfile(bf)
global_scaleform_db.open()

path = r"C:\Users\vardo\Documents\pyDXHR\playground\scaleform"
global_scaleform_db.dump_to_folder(path)

breakpoint()
