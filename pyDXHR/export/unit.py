"""


"""

import shutil
from tqdm import tqdm

import kaitaistruct
from pathlib import Path

from Bigfile import Bigfile
from pyDXHR.DRM import DRM
from pyDXHR.DRM.Section import Material, RenderResource
from pyDXHR.DRM.unit import UnitDRM
from pyDXHR.export import gltf
import tempfile


def from_drm(
    drm: UnitDRM,
    bigfile: Bigfile,
    save_to: Path | str,
    scale: float = 1.0,
    z_up: bool = False,
    **kwargs,
) -> None:
    if drm.is_masterunit:
        pbar = tqdm(drm.linked_drm_list)
        for subunit in pbar:
            subunit_drm = UnitDRM.from_bigfile(subunit, bigfile)
            subunit_drm.open()
            pbar.set_description(f"Exporting {subunit_drm.name}")

            from_drm(subunit_drm, bigfile, save_to, scale, z_up, **kwargs)
        return

    if len(Path(save_to).suffix) != 0:
        save_to = Path(save_to).parent
        save_to.mkdir(parents=True, exist_ok=True)

    library_path = Path(save_to) / "library"
    library_path.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.gettempdir()) / "pyDXHR"
    temp_dir.mkdir(parents=True, exist_ok=True)

    if library_path.is_dir():
        library_items = set(i.stem for i in library_path.glob("*.gltf"))
    else:
        library_items = set()

    # stream data
    stream_file_list = []
    if kwargs.get("stream", True):
        stream_gltf_list = []
        stream_tex_list = []
        stream_mat_list = []
        if len(drm.streamgroup_map):
            for (
                streamgroup_path,
                streamgroup_name,
            ), trs in drm.streamgroup_map.items():
                stream_drm = DRM.from_bigfile(
                    rf"streamgroups\{streamgroup_name}.drm", bigfile
                )
                stream_drm.open()
                try:
                    stream_drm.parse_filenames(bigfile)
                except FileNotFoundError:
                    pass

                mat_list = Material.from_drm(stream_drm)
                for mat in mat_list:
                    mat.read()
                stream_mat_list.extend(mat_list)

                tex_list = RenderResource.from_drm(stream_drm)
                for tex in tex_list:
                    tex.read()
                stream_tex_list.extend(tex_list)

                for sec in stream_drm.sections:
                    stream_gltf = gltf.to_temp(sec)
                    if stream_gltf is not None:
                        stream_gltf_list.append(stream_gltf)

            stream_save_to = Path(save_to) / (drm.name.replace(".drm", "") + "_streams.gltf")
            gltf.merge_gltf(
                gltf_list=stream_gltf_list,
                save_to=stream_save_to,
                mat_list=stream_mat_list,
                tex_list=stream_tex_list,
                drm_name=drm.name.replace(".drm", ""),
                scale=scale,
                z_up=z_up
            )
            stream_file_list.append(stream_save_to)

    # internal material + texture data (for int_imf + cells)
    mat_list = []
    tex_list = []
    if kwargs.get("cell", True) or kwargs.get("int_imf", True):
        mat_list = Material.from_drm(drm)
        for mat in mat_list:
            mat.read()

        tex_list = RenderResource.from_drm(drm)
        for tex in tex_list:
            tex.read()

    # internal data (cells/internal stream data)
    if kwargs.get("cell", True):
        cell_gltf_list = []
        if len(drm.cell_map):
            for (cell_name, cell_sec_id), sec in drm.cell_section_data.items():
                cell_gltf = gltf.to_temp(sec)
                cell_gltf_list.append(cell_gltf)

            gltf.merge_gltf(gltf_list=cell_gltf_list,
                            save_to=Path(save_to) / (drm.name.replace(".drm", "") + "_cells.gltf"),
                            mat_list=mat_list,
                            tex_list=tex_list,
                            drm_name=f"{drm.name.replace('.drm', '')}_cell",
                            scale=scale,
                            z_up=z_up
                            )

    # IMF data
    if kwargs.get("int_imf", True) or kwargs.get("ext_imf", True):
        if not len(drm.int_imf_map) or not len(drm.ext_imf_map):
            drm.read_imfs()

        if kwargs.get("int_imf", True):
            for sec_id, _ in drm.int_imf_map.items():
                if Path(f"{sec_id:08X}.gltf").stem in library_items:
                    continue

                imf_gltf = gltf.to_temp(drm.get_section_from_id(sec_id))
                if imf_gltf:

                    # fix the buffers
                    for buff in imf_gltf.buffers:
                        if buff.extras.get("name", "empty") != "empty":
                            buffer_file = temp_dir / buff.uri
                            shutil.copy(buffer_file, library_path)

                    # fix images and textures, if available
                    # breakpoint()

                    imf_gltf.save(library_path / f"{sec_id:08X}.gltf")

            gltf.merge_using_library(
                library_path=library_path,
                loc_table=drm.int_imf_map,
                save_to=Path(save_to)
                / (drm.name.replace(".drm", "") + "_int_imf.gltf"),
                unit_name=drm.name.replace(".drm", "") + "_int_imf",
                scale=scale,
                z_up=z_up,
            )

        if kwargs.get("ext_imf", True):
            for imf_name, _ in drm.ext_imf_map.items():
                if Path(imf_name).stem in library_items:
                    continue

                imf_drm = DRM.from_bigfile(imf_name, bigfile)
                imf_drm.open()

                try:
                    gltf.from_drm(
                        imf_drm,
                        save_to=library_path / (Path(imf_name).stem + ".gltf"),
                        scale=0.002,
                        z_up=True,
                        skip_textures=True
                    )
                except kaitaistruct.KaitaiStructError:
                    continue
                except Exception as e:
                    breakpoint()

            gltf.merge_using_library(
                library_path=library_path,
                loc_table=drm.ext_imf_map,
                save_to=Path(save_to)
                / (drm.name.replace(".drm", "") + "_ext_imf.gltf"),
                unit_name=drm.name.replace(".drm", "") + "_ext_imf",
                scale=scale,
                z_up=z_up,
            )

    # object data
    if kwargs.get("obj", True):
        if not len(drm.obj_map):
            drm.read_objects()

        object_list = [
            line.split(",")
            for line in bigfile.read("objectlist.txt").decode("utf-8").split("\r\n")
        ]
        object_list = {int(line[0]): line[1] for line in object_list if len(line) == 2}
        parsed_object_map = {
            object_list[obj_id]: trs_list for obj_id, trs_list in drm.obj_map.items()
        }

        for obj_name, _ in parsed_object_map.items():
            if obj_name in library_items:
                continue

            obj_drm = DRM.from_bigfile(obj_name + ".drm", bigfile)
            obj_drm.open()

            try:
                gltf.from_drm(
                    obj_drm,
                    save_to=library_path / (obj_name + ".gltf"),
                    scale=0.002,
                    z_up=True,
                    skip_textures=True
                )
            except kaitaistruct.KaitaiStructError:
                continue
            except:
                breakpoint()

        gltf.merge_using_library(
            library_path=library_path,
            loc_table=parsed_object_map,
            save_to=Path(save_to) / (drm.name.replace(".drm", "") + "_obj.gltf"),
            unit_name=drm.name.replace(".drm", "") + "_obj",
            scale=scale,
            z_up=z_up,
        )

    # gltf.merge_all(
    #     save_to=Path(save_to) / (drm.name.replace(".drm", "") + ".gltf"),
    #     drm_name=drm.name.replace(".drm", ""),
    #     scale=scale,
    #     z_up=z_up,
    #     gltf_files=[
    #         Path(save_to) / (drm.name.replace(".drm", "") + "_cells.gltf"),
    #         Path(save_to) / (drm.name.replace(".drm", "") + "_int_imf.gltf"),
    #         Path(save_to) / (drm.name.replace(".drm", "") + "_ext_imf.gltf"),
    #         Path(save_to) / (drm.name.replace(".drm", "") + "_obj.gltf"),
    #         *stream_file_list,
    #     ],
    # )
