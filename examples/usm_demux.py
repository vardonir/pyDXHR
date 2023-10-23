from pyDXHR.Bigfile import Bigfile
from pyDXHR.USM import demux

bf = Bigfile.from_env()
bf.open()

usm_path = r"design_database\videos\cinematics\final_cinematics\cut_01_shq0_3_woundedheroreturns\dxni_115_v10-woundedheroreturns.usm"  # noqa

demux(bf, usm_path, r"C:\Users\vardo\Documents\pyDXHR\playground\usm")

breakpoint()