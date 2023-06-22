from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.Sections import RenderMesh
from pathlib import Path
import kaitaistruct
from tqdm import tqdm
import warnings
import pygltflib as gl
import shutil
import os
from dotenv import load_dotenv

load_dotenv()

arc = Archive()
arc.deserialize_from_env()
# arc.deserialize_from_file(r"F:\Games\Deus Ex HRDC\BIGFILE.000")

file_list = r"F:\Projects\pyDXHR\external\filelist_generic.txt"
file_list = set(Path(file_list).read_text().split("\n"))

output_dir = r"F:\Projects\pyDXHR\output\blender"
texlib = os.getenv("PYDXHR_TEXLIB")

# texture_dest = Path(output_dir) / "textures"
# texture_dest.mkdir(parents=True, exist_ok=True)


# textures + materials
def materials(limit=-1):
    from pyDXHR.cdcEngine.Sections import Material

    processed_materials = set()
    matlib_gltf = gl.GLTF2()

    tex_dict = {}
    for im in Path(texlib).rglob("*.png"):
        # shutil.copy(im, texture_dest / im.name)
        index = len(matlib_gltf.images)

        image = gl.Image(
            name=im.stem,
            uri=str(im),
            mimeType="image/png"
        )

        tex = gl.Texture(
            source=index,
            name=im.stem,
        )
        tex_dict[im.stem] = index
        matlib_gltf.images.append(image)
        matlib_gltf.textures.append(tex)

    did_break = False
    for file in tqdm(file_list):
        if len(file) == 0:
            continue

        data = arc.get_from_filename(file)
        if data is None:
            continue

        drm = DRM()
        des = drm.deserialize(data)

        if not des:
            continue

        if did_break:
            break

        mtl_set = Material.deserialize_drm(drm)
        for mtl in mtl_set.difference(processed_materials):

            if len(mtl.Diffuse):
                pbr = gl.PbrMetallicRoughness(
                    baseColorTexture=gl.TextureInfo(
                        index=tex_dict.get(f"{mtl.Diffuse[0][0]:x}".rjust(8, '0'))
                    )
                )
            else:
                pbr = None

            if len(mtl.Normal):
                norm = gl.NormalMaterialTexture(
                    index=tex_dict.get(f"{mtl.Normal[0][0]:x}".rjust(8, '0'))
                )
            else:
                norm = None

            gltf_mat = gl.Material(
                extras={k: str(v) for k, v in mtl.to_json().items()},
                name=mtl.Name[-4:].upper(),
                alphaCutoff=0.0,
                alphaMode=gl.MASK if mtl.HasAlpha else gl.OPAQUE,
                doubleSided=False,
                pbrMetallicRoughness=pbr,
                normalTexture=norm,
            )

            gltf_mat.extras["needs_checking"] = 1 if mtl.NeedsChecking else 0
            gltf_mat.extras["colors"] = str(mtl.FlatColors)

            matlib_gltf.materials.append(gltf_mat)
            processed_materials.add(mtl)

            if limit != -1:
                if len(processed_materials) > limit:
                    did_break = True
                    break

    print(f"Saving {len(matlib_gltf.materials)} materials...")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        matlib_gltf.save(Path(output_dir) / "materials.gltf")



# unit_list = [Path(u).stem + ".drm" for u in arc.unit_list]
# obj_list = set(o + ".drm" for o in arc.object_list.values())

# generate OBJs
# obj_dir = Path(output_dir) / "obj"
# obj_dir.mkdir(parents=True, exist_ok=True)
# for obj in tqdm(obj_list):
#     data = arc.get_from_filename(obj)
#     if data is None and obj in file_list:
#         breakpoint()
#     if data is None:
#         continue
#
#     drm = DRM()
#     des = drm.deserialize(data)
#     if des:
#         try:
#             rms = RenderMesh.deserialize_drm(drm)
#         except kaitaistruct.ValidationNotEqualError as e:
#             continue
#         else:
#             for rm in rms:
#                 rm.to_gltf(save_to=obj_dir / Path(obj).stem)

# generate external IMFs
# TODO

# generate stream objects (external RenderTerrains)

# generate internal IMFs + cells + location maps
# for unit in unit_list:
#     data = arc.get_from_filename(unit)
#     if data is None and unit in file_list:
#         breakpoint()

# do the same for scenarios

if __name__ == "__main__":
    materials(limit=5)

    breakpoint()
