from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pathlib import Path
from tqdm import tqdm
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
from pyDXHR.cdcEngine.Sections.RenderResource import RenderResource
from pyDXHR.Export.DDSWriter import OutputFormat


pc_arc = Archive()
pc_arc.deserialize_from_env("PC_BASE")

ps3_arc = Archive()
ps3_arc.deserialize_from_env("PS3_BASE")

file_list = r"F:\Projects\pyDXHR\external\filelist_generic.txt"
file_list = set(Path(file_list).read_text().split("\n"))

directory = Path(r"F:\Projects\pyDXHR\playground\texture_comparison")

# units
# item_list = [Path(u).stem + ".drm" for u in pc_arc.unit_list]

# imfs
imf_list = set(o for o in file_list if len(Path(o).parts) > 1 and Path(o).parts[0] == "imf")


def scan_items(it_list):
    texture_directory = {}

    for it in tqdm(it_list):
        pc_data = pc_arc.get_from_filename(it)
        ps3_data = ps3_arc.get_from_filename(it)

        if pc_data is not None:
            pc_drm = DRM()
            ps3_drm = DRM()

            des = ps3_drm.deserialize(ps3_data, archive=ps3_arc)
            if not des:
                continue

            des = pc_drm.deserialize(pc_data)
            if not des:
                continue

            pc_texs = [sec for sec in pc_drm.Sections if sec.Header.SectionType == SectionType.RenderResource]
            ps3_texs = [sec for sec in ps3_drm.Sections if sec.Header.SectionType == SectionType.RenderResource]

            if len(ps3_texs) != len(pc_texs):
                print(f"Texture count mismatch for {it}")
                continue

            for ps3, pc in zip(ps3_texs, pc_texs):
                pc_rm = RenderResource(section=pc)
                ps3_rm = RenderResource(section=ps3)

                if pc_rm.ID in texture_directory:
                    continue
                texture_directory[pc_rm.ID] = ps3_rm.HeaderName

                # if ps3_rm.HeaderName in texture_directory:
                #     continue
                # texture_directory[ps3_rm.HeaderName] = (pc_rm.ID, ps3_rm.ID)
                # filename = Path(ps3_rm.HeaderName).parts[-1].replace("|", "__")
                # dest = directory / filename
                # dest.mkdir(parents=True, exist_ok=True)
                # pc_rm.to_file(OutputFormat.TGA, save_to=dest / f"PC_{pc_rm.ID}.tga")
                # ps3_rm.to_file(OutputFormat.TGA, save_to=dest / f"PS3_{ps3_rm.ID}.tga")

    import json
    with open(directory / "texture_directory.json", "w") as f:
        json.dump(texture_directory, f, indent=2)


if __name__ == "__main__":
    scan_items(imf_list)
