from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import CompressedDRM
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM
from pathlib import Path
from tqdm import tqdm

arc = Archive()
arc.deserialize_from_env()

# cdrm_bytes = arc.get_from_filename("det_city_sarif.drm")
# decompressed = CompressedDRM.decompress(cdrm_bytes, return_as_bytes=True)

units = set([Path(unit).parts[-1] + ".drm" for unit in arc.unit_list if "game" in unit])

file_list = r"..\external\filelist_generic.txt"
file_list = Path(file_list).read_text().split("\n")

imfs_in_filelist = set([f for f in file_list if len(Path(f).parts) > 1 and Path(f).parts[0] == "imf"])
units_in_filelist = units.intersection(file_list)
not_drm = set([f for f in file_list if Path(f).suffix != ".drm"])
shaderlibs = set([f for f in file_list if len(Path(f).parts) > 1 and Path(f).parts[0] == "shaderlibs"])
stream_groups = set([f for f in file_list if len(Path(f).parts) > 1 and Path(f).parts[0] == "streamgroups"])

the_rest = set(file_list)\
    .difference(imfs_in_filelist)\
    .difference(not_drm)\
    .difference(shaderlibs)\
    .difference(stream_groups)
#     .difference(units_in_filelist)

# string_to_look_for = "imf\\"
string_to_look_for = r"s_scn_det1_city_sarif_det_city_sarif"

for f in tqdm(the_rest):
    if len(f):
        cdrm_bytes = arc.get_from_filename(f)
        if cdrm_bytes:
            decompressed = CompressedDRM.decompress(cdrm_bytes, return_as_bytes=True)

            if string_to_look_for in decompressed.decode("latin1"):
                drm = DRM()
                drm.deserialize(cdrm_bytes)
                breakpoint()
