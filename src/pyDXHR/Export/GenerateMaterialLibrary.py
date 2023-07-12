from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pathlib import Path
from tqdm import tqdm
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM
from pyDXHR.cdcEngine.Sections import Material

pc_arc = Archive()
pc_arc.deserialize_from_env()

ps3_arc = Archive()
ps3_arc.deserialize_from_env("PS3_BASE")

file_list = r"F:\Projects\pyDXHR\external\filelist_generic.txt"
file_list = set(Path(file_list).read_text().split("\n"))

output_dir = r"F:\Projects\pyDXHR\output\blender"

# obj_list = set(o + ".drm" for o in pc_arc.object_list.values())
item_list = set(o for o in file_list if len(Path(o).parts) > 1 and Path(o).parts[0] == "imf")
# item_list = set(o for o in file_list if o.startswith("stream"))
# unit_list = [Path(u).stem + ".drm" for u in arc.unit_list]

mtl_names = {}
mtl_database = {}
for item in tqdm(item_list):
    # if "global" in item:
    #     continue
    #
    # # for streams and units:
    # if "det" not in item:
    #     continue

    pc_data = pc_arc.get_from_filename(item)
    ps3_data = ps3_arc.get_from_filename(item)
    if ps3_data is None:
        continue

    ps3_drm = DRM()
    des = ps3_drm.deserialize(ps3_data, archive=ps3_arc)
    if not des:
        continue

    pc_drm = DRM()
    des = pc_drm.deserialize(pc_data)
    if not des:
        continue

    ps3_mtl_set = Material.deserialize_drm(ps3_drm, archive=ps3_arc, texture_library=None, use_libraries=False, only_submat3=True)
    pc_mtl_set = Material.deserialize_drm(pc_drm, only_submat3=True)

    # if this assert fails, the entire 1:1 material idea is gone
    assert len(ps3_mtl_set) == len(pc_mtl_set)

    # for each material in the DRM
    for ps3, pc in zip(ps3_mtl_set, pc_mtl_set):

        if pc.ID in mtl_database:
            continue
        else:
            mtl_database[pc.ID] = {}

        if len(pc.submat3) != len(ps3.submat3):
            print(ps3.HeaderName)

        # for each texture in the material
        seen = []
        for ps3_s3, pc_s3 in zip(ps3.submat3, pc.submat3):
            pc_tex_id = pc_s3[0]

            if pc_tex_id in seen:
                continue
            seen.append(pc_tex_id)

            tex_name = ps3_arc.texture_list[ps3_s3[0]]

            if "diffu" in tex_name:
                ps3_tex_type = "d"
            elif "normal" in tex_name:
                ps3_tex_type = "n"
            elif "specul" in tex_name:
                ps3_tex_type = "s"
            elif "blend" in tex_name:
                ps3_tex_type = "b"
            elif "mask" in tex_name:
                ps3_tex_type = "m"
            elif "light" in tex_name:
                ps3_tex_type = "l"
            elif "|" in tex_name:
                ps3_tex_type = tex_name.split("|")[1][0]
            elif "poster" in tex_name:
                ps3_tex_type = "i"
            elif "decal" in tex_name:
                ps3_tex_type = "i"
            elif "billboard" in tex_name:
                ps3_tex_type = "i"
            elif "flat" in tex_name:
                ps3_tex_type = "c"
            elif "cube" in tex_name:
                ps3_tex_type = "q"
            elif "default_mat_txt" in tex_name:
                ps3_tex_type = "f"
            else:
                ps3_tex_type_temp = Path(tex_name).stem.split("_")[-1]
                if ps3_tex_type_temp not in {"d", "n", "s"}:
                    ps3_tex_type = "u"
                else:
                    ps3_tex_type = ps3_tex_type_temp

            if ps3_tex_type not in mtl_database[pc.ID]:
                mtl_database[pc.ID][ps3_tex_type] = []

            mtl_database[pc.ID][ps3_tex_type].append((tex_name, pc_s3[0]))

            if item not in mtl_names:
                mtl_names[item] = set()

            mtl_names[item].add((pc.ID, tex_name))
        # mtl_database[ps3.HeaderName] = pc

# import json
# with open(r"F:\Projects\pyDXHR\output\ps3\stream_mtl_database.json", "w") as f:
#     json.dump(mtl_database, f, indent=2)

breakpoint()
