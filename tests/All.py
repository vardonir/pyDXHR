from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pathlib import Path
from tqdm import tqdm

arc = Archive()
arc.deserialize_from_env("PS3_DC")

file_list = r"..\external\filelist_generic.txt"
file_list = Path(file_list).read_text().split("\n")

destination = r"F:\Projects\pyDXHR\output\ps3"

pair_list = set()
for file in tqdm(file_list):
    data = arc.get_from_filename(file)
    if data:
        drm = DRM()
        des = drm.deserialize(data, archive=arc)

        if des:
            for head, dat in zip(drm.Header.SectionHeaders, drm.SectionData):
                if head.Name is not None:
                    asset_path = Path(head.Name.replace(":", "/"))
                    path = Path(destination) / asset_path

                    with open(path, "wb") as f:
                        f.write(dat)

                pairs = set((h.SectionType.value, h.SectionSubtype.value) for h in drm.Header.SectionHeaders)
                pair_list.add(pairs)

breakpoint()
