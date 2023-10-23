from pyDXHR.DRM import DRM
from pyDXHR.Bigfile import Bigfile, filelist
from pyDXHR.export import gltf
from pathlib import Path
from tqdm import tqdm

imf_lib_dest = r"C:\Users\vardo\Documents\pyDXHR\playground\imf_library"

bf = Bigfile.from_env()
bf.open()

fl = filelist.read_filelist("pc-w")

imf_list = [path for _, path in fl.items() if path.startswith("imf")]

for imf in tqdm(imf_list):
    # breakpoint()
    try:
        drm = DRM.from_bigfile(imf, bf)
        drm.open()
    except:
        continue

    try:
        gltf.from_drm(drm,
                      save_to=Path(imf_lib_dest) / (imf[:-4] + ".gltf"),
                      scale=0.002, z_up=True
                      )
    except:
        continue
