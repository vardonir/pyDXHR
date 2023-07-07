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

detroit_only = True

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


# generate OBJs
def objects(limit=-1):
    obj_list = set(o + ".drm" for o in arc.object_list.values())
    if obj_list != -1:
        obj_list = list(obj_list)[:limit]

    obj_dir = Path(output_dir) / "obj"
    obj_dir.mkdir(parents=True, exist_ok=True)
    for obj in tqdm(obj_list):
        data = arc.get_from_filename(obj)
        if data is None:
            continue

        drm = DRM()
        des = drm.deserialize(data)
        if des:
            try:
                rms = RenderMesh.deserialize_drm(drm)
            except kaitaistruct.ValidationNotEqualError as e:
                continue
            else:
                for rm in rms:
                    rm.to_gltf(save_to=obj_dir / Path(obj).stem)


# generate external IMFs
def imfs(limit=-1):
    imf_list = set(o for o in file_list if len(Path(o).parts) > 1 and Path(o).parts[0] == "imf")
    if imf_list != -1:
        imf_list = list(imf_list)[:limit]

    imf_dir = Path(output_dir) / "imf"
    imf_dir.mkdir(parents=True, exist_ok=True)
    for imf in tqdm(imf_list):
        data = arc.get_from_filename(imf)
        if data is None:
            continue

        drm = DRM()
        des = drm.deserialize(data)
        if des:
            try:
                rms = RenderMesh.deserialize_drm(drm)
            except kaitaistruct.ValidationNotEqualError as e:
                continue
            else:
                for rm in rms:
                    rm.to_gltf(save_to=imf_dir / Path(imf).stem)


# generate stream objects (external RenderTerrains)
def streamobjects(limit=-1):
    streams = set(o for o in file_list if o.startswith("stream"))
    if detroit_only:
        streams = [s for s in streams if "det" in s]

    if limit != -1:
        streams = streams[:limit]

    stream_dir = Path(output_dir) / "stream"
    stream_dir.mkdir(parents=True, exist_ok=True)
    for stream in tqdm(streams):
        data = arc.get_from_filename(stream)
        if data is None:
            continue

        drm = DRM()
        des = drm.deserialize(data)
        if des:
            try:
                rms = RenderMesh.deserialize_drm(drm)
            except kaitaistruct.ValidationNotEqualError as e:
                continue
            else:
                for rm in rms:
                    rm.to_gltf(save_to=stream_dir / Path(stream).stem)


# generate internal IMFs + cells
def internal_meshes(unit=None):
    from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM

    unit_list = [Path(u).stem + ".drm" for u in arc.unit_list]
    out_dir = Path(output_dir) / "unit"
    out_dir.mkdir(parents=True, exist_ok=True)

    if unit is None:
        for unit in unit_list:
            if detroit_only and "det" not in unit:
                continue

            data = arc.get_from_filename(unit)
            if data is None:
                breakpoint()
            else:
                internal_meshes(unit=unit)
    else:
        data = arc.get_from_filename(unit)
        drm = UnitDRM()

        # we only want internal RT and RM + collision
        drm.deserialize(
            data,
            archive=arc,

            skip_ext_imf=True,
            stream=False,
            obj=False,
            cell=True,
            occlusion=False,
            collision=False,
        )
        drm.to_gltf(
            save_to=out_dir / Path(unit).stem,
            flat_folders=True,
        )


# generate location tables for each unit
def location_table(unit=None):
    from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM

    unit_list = [Path(u).stem + ".drm" for u in arc.unit_list]
    out_dir = Path(output_dir) / "loc"
    out_dir.mkdir(parents=True, exist_ok=True)

    if unit is None:
        for unit in unit_list:
            if detroit_only and "det" not in unit:
                continue

            data = arc.get_from_filename(unit)
            if data is None:
                continue
            else:
                location_table(unit=unit)
    else:
        data = arc.get_from_filename(unit)
        drm = UnitDRM()

        drm.deserialize(
            data,
            archive=arc
        )
        drm.to_csv(
            save_to=out_dir / (Path(unit).stem + ".csv"),
        )


if __name__ == "__main__":
    location_table()
    # breakpoint()
