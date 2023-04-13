import csv
import numpy as np
from typing import Optional
from pathlib import Path


def guess_materials(int1a, int1b1, int1b2, int2, byte1, tbind, byte3, byte4):
    # the same handwavy bullshit. copy-pasted from pyDXHR for now

    if byte1 == 96:
        return "cubemap"

    if int2 == 4:
        return "blend"
    else:
        if byte1 == 32:
            return "diffuse"
        elif byte1 == 128:
            return "normal"


def check_unit_path():
    if len(list(Path(cdc_unit_path).rglob("*.gltf"))):
        pass
    else:
        raise Exception("Read the note.")


def import_gltf_data(mesh_filter: Optional[str] = None):
    tasks = []
    for obj_path in Path(cdc_unit_path).rglob("*.gltf"):
        if mesh_filter and mesh_filter not in str(obj_path):
            continue
        else:
            asset_import_task = unreal.AssetImportTask()
            asset_import_task.filename = str(obj_path)
            asset_import_task.destination_path = ue_import_path + f"{obj_path.stem}/"
            asset_import_task.automated = True
            tasks.append(asset_import_task)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_tools.import_asset_tasks(tasks)


def recompile_materials():
    asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()
    material_editing_library = unreal.MaterialEditingLibrary

    material_path = asset_reg.get_assets_by_path(ue_material_path, recursive=True)
    material_assets = asset_reg.run_assets_through_filter(material_path, unreal.ARFilter(class_names=["Material"]))

    arr = np.loadtxt(pydxhr_matlib, delimiter=",", dtype=int)

    with unreal.ScopedSlowTask(len(material_assets)) as ue_task:
        ue_task.make_dialog(can_cancel=True)

        for mat in material_assets:
            mat_id_hex = str(mat.asset_name).split("_")[1]
            mat_id_dec = int(mat_id_hex, 16)

            tex_arr = arr[np.where(arr[:, 0] == mat_id_dec)]
            seen = []
            for idx, (tex_id_dec, tex_info) in enumerate(zip(tex_arr[:, 1], tex_arr[:, 2:])):
                if tex_id_dec in seen:
                    continue

                tex_id_prefhex = "T_" + f"{tex_id_dec:x}".rjust(8, '0')
                mat_type = guess_materials(*tex_info)

                loaded_mat = unreal.EditorAssetLibrary.load_asset(mat.package_name)
                node_tex = material_editing_library.create_material_expression(loaded_mat,
                                                                               unreal.MaterialExpressionTextureSampleParameter2D,
                                                                               node_pos_x=-400,
                                                                               node_pos_y=200 * idx)

                texture_asset = unreal.load_asset(ue_texture_path + tex_id_prefhex)

                node_tex.set_editor_property("Desc", f"{mat_type} | {str(tex_info)}")
                node_tex.set_editor_property("texture", texture_asset)
                seen.append(tex_id_dec)


def categorize_assets():
    asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()

    import_path = asset_reg.get_assets_by_path(ue_import_path, recursive=True)
    mesh_assets = asset_reg.run_assets_through_filter(import_path, unreal.ARFilter(class_names=["StaticMesh"]))
    material_assets = asset_reg.run_assets_through_filter(import_path, unreal.ARFilter(class_names=["Material"]))

    # look for the materials that need to be consolidated
    found_materials = []
    materials_for_consolidation = []

    with unreal.ScopedSlowTask(len(material_assets)) as ue_task:
        ue_task.make_dialog(can_cancel=True)

        for mat in material_assets:
            mat_id_hex = str(mat.asset_name).split("_")[1]
            if len(mat_id_hex) != 8:  # look for materials that were duplicated on import
                consolidate_to = ue_material_path + f"M_{mat_id_hex[:8]}"
                materials_for_consolidation.append((consolidate_to, mat.package_name))

            if mat_id_hex in found_materials:
                consolidate_to = ue_material_path + f"M_{mat_id_hex}"
                materials_for_consolidation.append((consolidate_to, mat.package_name))
            else:
                found_materials.append(mat_id_hex)
                unreal.EditorAssetLibrary.rename_asset(mat.package_name, ue_material_path + str(mat.asset_name))

    with unreal.ScopedSlowTask(len(materials_for_consolidation)) as ue_task:
        ue_task.make_dialog(can_cancel=True)

        for con_to, con_from in materials_for_consolidation:
            original_asset = unreal.EditorAssetLibrary.load_asset(con_from)
            replacement_asset = unreal.EditorAssetLibrary.load_asset(con_to)
            unreal.EditorAssetLibrary.consolidate_assets(replacement_asset, [original_asset])

    # rename the textures, because asset_import_task.destination_name doesnt seem to work?
    tex_import_path = asset_reg.get_assets_by_path(ue_texture_path, recursive=True)
    texture_assets = asset_reg.run_assets_through_filter(tex_import_path, unreal.ARFilter(class_names=["Texture2D"]))

    with unreal.ScopedSlowTask(len(texture_assets)) as ue_task:
        ue_task.make_dialog(can_cancel=True)

        for tex in texture_assets:
            unreal.EditorAssetLibrary.rename_asset(tex.package_name, ue_texture_path + f"T_{tex.asset_name}")

    # move the meshes to the right directory
    # the importer is designed to work with one unit at a time for now - there shouldnt be any conflicting meshes
    # at this point
    with unreal.ScopedSlowTask(len(mesh_assets)) as ue_task:
        ue_task.make_dialog(can_cancel=True)

        for mesh in mesh_assets:
            unreal.EditorAssetLibrary.rename_asset(mesh.package_name, ue_static_mesh_path + str(mesh.asset_name))

    # delete the import folder
    unreal.EditorAssetLibrary.delete_directory(ue_import_path)


def place_actors():
    location_directory = {}
    with open(Path(cdc_unit_path) / "locations.csv", "r") as csvfile:
        location_reader = csv.reader(csvfile)
        for row in location_reader:
            if row[0] not in location_directory:
                location_directory[row[0]] = []
            location_directory[row[0]].append([row[1:4], row[4:7], row[7:10]])

    asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()

    static_mesh_path = asset_reg.get_assets_by_path(ue_static_mesh_path, recursive=True)
    mesh_assets = asset_reg.run_assets_through_filter(static_mesh_path, unreal.ARFilter(class_names=["StaticMesh"]))

    with unreal.ScopedSlowTask(len(mesh_assets)) as ue_task:
        ue_task.make_dialog(can_cancel=True)

        for mesh in mesh_assets:
            base_object = unreal.load_asset(mesh.package_name)

            for entry in location_directory[str(mesh.asset_name)]:
                loc, rot, scl = entry
                loc = unreal.Vector(*[float(i) for i in loc])
                rot = unreal.Rotator(*[float(i) for i in rot])
                scl = unreal.Vector(*[float(i) for i in scl])

                spawned_actor = unreal.EditorActorSubsystem().spawn_actor_from_object(base_object, loc, rot)
                spawned_actor.set_actor_scale3d(scl)


def import_texture_library():
    tasks = []
    for obj_path in (Path(cdc_unit_path) / "textures").rglob("*.png"):
        asset_import_task = unreal.AssetImportTask()
        asset_import_task.filename = str(obj_path)
        asset_import_task.destination_path = ue_texture_path
        asset_import_task.automated = True
        asset_import_task.replace_existing = True
        tasks.append(asset_import_task)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_tools.import_asset_tasks(tasks)


def flip():
    pass


def main(**kwargs):
    # step -1: pyDXHR
    # the meshes need to be created using pyDXHR separately from UE5 for now - ideally the entire level will be imported
    # straight from UE5's python console, but UE5 uses py3.9 and pyDXHR requires 3.10, and i don't feel like
    # recompiling UE5 again, so...
    check_unit_path()

    # step 0: test print for checking
    current_level = unreal.LevelEditorSubsystem().get_current_level()
    print("Importing to", current_level.get_full_name())

    # step X: bulk import meshes and materials to a temporary folder
    # mesh filter is just a way to import only a specific folder from whatever pyDXHR generated - useful for debugging
    # large units
    import_gltf_data(mesh_filter=kwargs.get("mesh_filter"))

    # step X: bulk import texture library
    # see the next step for an explanation why this is imported separately.
    import_texture_library()

    # step X: fix asset locations
    categorize_assets()

    # step X: material cleanup
    # since the texture/material auto-assignment is incomplete and im sick of trying to figure it out for now,
    # this part just looks for the material data in the matlib generated by pydxhr, attaches the images given the
    # right material, makes a feeble attempt at auto-assignment, and then just leaves the rest there to hang out
    # in the material, but not attached to any node
    recompile_materials()

    # step ?: placement
    # read the location directory and place the actors according to the locations specified in the unit DRM
    place_actors()

    # step ??: (╯°□°)╯︵ ┻━┻
    # flip that mf
    flip()

    # step ?: profit???
    print("DONE!")

if __name__ == "__main__":
    cdc_unit_path = r"F:\Game_Rips\deus-ex-human-revolution\pyDXHR\preprocessed\unit\det_city_tunnel1"
    pydxhr_matlib = r"F:\Game_Rips\deus-ex-human-revolution\pyDXHR\material_library\pc_base_matlib.csv"

    ue_import_path = '/Game/ImportTest/'
    ue_static_mesh_path = '/Game/Meshes/'
    ue_texture_path = '/Game/Textures/'
    ue_material_path = '/Game/Materials/'

    try:
        import unreal
    except ModuleNotFoundError:
        print("Please run this script within Unreal Engine")
    else:
        main()
