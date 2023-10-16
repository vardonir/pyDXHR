from pyDXHR.DRM import DRM
from pyDXHR.Bigfile import Bigfile
from pyDXHR.export import gltf
from pathlib import Path
from tqdm import tqdm

bf = Bigfile.from_env()
bf.open()

obj_list = bf.read_data_by_name("objectlist.txt").decode("utf-8").split("\n")
dest = r"C:\Users\vardo\Documents\pyDXHR\playground\obj_library"

for i, obj in tqdm(enumerate(obj_list)):
    if i == 0:
        continue
    if i == len(obj_list) - 1:
        continue

    _, obj_name = obj.split(",")
    # obj_id = int(obj_id.strip())
    obj_name = obj_name.strip() + ".drm"

    try:
        drm = DRM.from_bigfile(obj_name, bf)
        drm.open()
    except:
        continue

    try:
        gltf.from_drm(drm,
                      save_to=Path(dest) / (obj_name[:-4] + ".gltf"),
                      scale=0.002, z_up=True
                      )
    except:
        continue

breakpoint()
