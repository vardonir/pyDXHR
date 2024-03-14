"""
Dump all material and texture data
Status: In Progress
    compiled version throws error about missing file lists
"""

# go through all the material sections in the game
# compile the material IDs
# write that to a json file with the texture IDs

# go through all the texture sections in the game
# convert everything to TGA or PNG or DDS

# if the names are available, create another file with that

# input - bigfile.000 for PC, cache.000 for ps3
from pathlib import Path
from tqdm import tqdm
from pyDXHR.Bigfile import Bigfile, console_filenames
from pyDXHR.DRM import DRM
from pyDXHR.DRM.Section import RenderResource, Material
import json


def unpack(path_to_000, unpacked_destination):
    bf = Bigfile.from_path(path_to_000)
    bf.open()

    mtl_data = {}
    mtl_ids = set()
    textures_dir = Path(unpacked_destination) / "textures"
    textures_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for (h, _), entry in tqdm((bf.named_entries | bf.unknown_entries).items()):
        count += 1
        # if count == 10: break

        try:
            drm = DRM.from_bigfile(h, bf)
            drm.open()
        except Exception:
            # not a DRM
            continue
        else:
            for rr in RenderResource.from_drm(drm):
                try:
                    tex = rr.read()
                except Exception as e:
                    print(e)
                    continue

                if (textures_dir / (tex.Name + ".png")).is_file():
                    continue
                else:
                    tex.to_png(textures_dir)

            for mtl in Material.from_drm(drm):
                mtl.read()
                name = f"M_{mtl.section_id:08X}"
                mtl_ids.add(mtl.section_id)

                if name in mtl_data:
                    continue
                else:
                    mtl_entry = {
                        "diffuse": set(),
                        "normal": set(),
                        "specular": set(),
                        "unknown": set(),
                        "mask": set(),
                        "blend": set(),
                        "alpha": 0,
                    }

                alpha = 0
                for mat_tex in mtl.material_tex_list:
                    if mat_tex.submat_index == 1:
                        alpha = 1

                    match mat_tex.texture_class:
                        case 0x20:
                            mtl_entry["diffuse"].add(f"{mat_tex.texture_id:08X}")
                        case 0x80:
                            mtl_entry["normal"].add(f"{mat_tex.texture_id:08X}")

                mtl_data[f"M_{mtl.section_id:08X}"] = {
                    k: list(v) for k, v in mtl_entry.items() if k != "alpha"
                }
                mtl_data[f"M_{mtl.section_id:08X}"] |= {"alpha": alpha}

    with open(Path(unpacked_destination) / "materials.json", "w") as f:
        json.dump(mtl_data, f, indent=2)

    if bf.platform != Bigfile.Platform.PC:
        texture_dict = console_filenames.textures_ids(bf)
        dtpdata_dict = console_filenames.dtpdata_ids(bf)
        named_materials = {id: dtpdata_dict[id] for id in mtl_ids}

        named_textures_dir = Path(unpacked_destination) / "named_textures"

        for tex in tqdm(textures_dir.rglob("*.png")):
            if tex.is_file():
                tex_id = int(tex.stem, 16)
                name = Path(texture_dict[tex_id].replace("|", "_")).parts[-1] + ".png"
                path = named_textures_dir / "/".join(
                    Path(texture_dict[tex_id].replace("|", "_")).parts[:-1]
                )
                path.mkdir(parents=True, exist_ok=True)
                try:
                    tex.rename(path / name)
                except FileExistsError:
                    continue

        named_mat_database = {}
        for mat_id, mat_path in named_materials.items():
            sanitized_mat_path = Path("/".join(Path(mat_path).parts[1:]))

            # if sanitized_mat_path not in named_mat_database:
            #     named_mat_database[sanitized_mat_path] = []

            mat_tex_data = mtl_data[f"M_{mat_id:08X}"]

            mtl_entry = {
                "diffuse": list(),
                "normal": list(),
                "specular": list(),
                "unknown": list(),
                "mask": list(),
                "blend": list(),
                "alpha": 0,
            }
            for identifier, tex_list in mat_tex_data.items():
                if identifier == "alpha":
                    mtl_entry[identifier] = tex_list
                    continue

                for tex_id in tex_list:
                    named_texture = texture_dict[int(tex_id, 16)].replace("|", "_")
                    mtl_entry[identifier].append(str(named_texture))

            named_mat_database[str(sanitized_mat_path)] = mtl_entry

        with open(Path(unpacked_destination) / "named_materials.json", "w") as f:
            json.dump(named_mat_database, f, indent=2)


if __name__ == "__main__":
    unpack(
        path_to_000=r"C:\Users\vardo\Documents\pyDXHR\bigfiles\DXHR\BIGFILE.000",
        unpacked_destination=r"C:\Users\vardo\Documents\pyDXHR\playground\mat_tex_unpack",
    )

    # import argparse
    #
    # parser = argparse.ArgumentParser(
    #     prog="pyDXHR Texture/Material dumper", description="Dump textures and material data"
    # )
    #
    # parser.add_argument(
    #     "source",
    #     metavar="source",
    #     type=str,
    # )
    #
    # parser.add_argument("-o", "--out", help="output directory", type=str, default=None)
    #
    # args = parser.parse_args()
    #
    # dest = None
    # if args.out is None:
    #     dest = Path(args.source).parent / "unpacked"
    # else:
    #     dest = Path(args.out)
    #
    # unpack(
    #     path_to_000=args.source,
    #     unpacked_destination=dest
    # )
    # exit(0)
