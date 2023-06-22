from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM
from pyDXHR.cdcEngine.DRM.MasterunitDRM import MasterunitDRM

arc = Archive()
arc.deserialize_from_env()

from pathlib import Path
masterunit_list = [Path(unit).stem for unit in arc.unit_list if "masterunit" in unit and "scenario" not in unit]

for m in masterunit_list:
    filename = m + ".drm"
    data = arc.get_from_filename(filename)
    if data:
        mu = MasterunitDRM(
            masterunit_name=filename,
            archive=arc,

            imf=False,
            stream=False,
            obj=True,
            occlusion=False,
            cell=False,
            collision=False,
        )
        obj_list = mu.list_objects()

    # drm = DRM()
    # drm.deserialize(data)

    breakpoint()

# from tqdm import tqdm
# for entry in tqdm(arc.Entries):
#     drm = DRM()
#     is_valid = drm.deserialize(arc.get_entry_data(entry))
#
#     if is_valid:
#         if len(drm.Header.OBJDependencies):
#             breakpoint()
# breakpoint()

