from pyDXHR.Bigfile import Bigfile, filelist
from pyDXHR.USM import demux

bf = Bigfile.from_env()
bf.open()

fl = filelist.read_filelist("pc-w")
usm_list = [path for _, path in fl.items() if path.endswith(".usm")]

for usm in usm_list:
    demux(bf, usm, r"F:\DXHR_bigfiles\USM")
