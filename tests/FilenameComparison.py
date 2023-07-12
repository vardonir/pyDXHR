from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pathlib import Path
from tqdm import tqdm
from pyDXHR.cdcEngine.Sections import Material

pc_arc = Archive()
pc_arc.deserialize_from_env()

ps3_arc = Archive()
ps3_arc.deserialize_from_env("PS3_BASE")

file_list = r"F:\Projects\pyDXHR\external\filelist_generic.txt"
file_list = set(Path(file_list).read_text().split("\n"))

# units
# item_list = [Path(u).stem + ".drm" for u in pc_arc.unit_list]

# imfs
item_list = set(o for o in file_list if len(Path(o).parts) > 1 and Path(o).parts[0] == "imf")



