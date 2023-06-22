from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM, ObjectType
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
from pyDXHR.cdcEngine.Sections import RenderMesh
from pathlib import Path
from tqdm import tqdm

arc = Archive()
arc.deserialize_from_env()

units = set([Path(unit).parts[-1] + ".drm" for unit in arc.unit_list if "game" in unit])

file_list = r"..\external\filelist_generic.txt"
file_list = Path(file_list).read_text().split("\n")

existing_units = units.intersection(file_list)

imfs = set()
for unit in tqdm(existing_units):
    pc_data = arc.get_from_filename(unit)
    unit_drm = UnitDRM()
    unit_drm.deserialize(
        pc_data,
        archive=arc,
        # imf=False,
        # skip_ext_imf=True,
        stream=False,
        obj=False,
        occlusion=False,
        cell=False,
        collision=False,
    )

    ext_imf = set(unit_drm.ObjectData.get(ObjectType.EXT_IMF, dict()).keys())
    if len(ext_imf.difference(file_list)) != 0:
        print(unit)
        print(ext_imf.difference(file_list))

    imfs = imfs.union(ext_imf)

imfs_in_filelist = set([f for f in file_list if len(Path(f).parts) > 1 and Path(f).parts[0] == "imf"])

imfs_not_in_units = [i for i in imfs_in_filelist.difference(imfs)]

breakpoint()

