from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pathlib import Path
from tqdm import tqdm

arc = Archive()
arc.deserialize_from_env("PS3_DC")

file_list = r"C:\Users\vardo\Documents\pyDXHR\filelist_generic.txt"
file_list = Path(file_list).read_text().split("\n")

destination = r"D:\Game_Rips\deus-ex-human-revolution\inflate"

pair_list = set()
for file in tqdm(file_list):
    data = arc.get_from_filename(file)
    if data:
        drm = DRM()
        des = drm.deserialize(data, archive=arc)

        if des:
            for head, dat in zip(drm.Header.SectionHeaders, drm.SectionData):
                if head.Name is not None:
                    asset_path = Path(head.Name.replace(":", "/").replace("|", "_"))
                    path = Path(destination) / asset_path
                    path.parent.mkdir(exist_ok=True,parents=True)

                    try:
                        with open(path, "wb") as f:
                            f.write(dat)
                    except:
                        print(path)

                pairs = set((h.SectionType.value, h.SectionSubtype.value) for h in drm.Header.SectionHeaders)
                pair_list.union(pairs)

print(pair_list)
