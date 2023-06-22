from pathlib import Path
import trimesh
import numpy as np


def categorize_by_bounds(gltf_file_directory, location_table, **kwargs):
    boxes = {}
    identity_trs = tuple(np.eye(4).astype(float).flatten().tolist())

    for path in Path(gltf_file_directory).rglob("*.gltf"):
        if "occlusion" in str(path):
            if path.stem in boxes:
                breakpoint()
            boxes[path.stem] = _get_model_bounds(path)

    # locations = {(it, tuple(trs_mat)): None for it, trs_mats in location_table.items() for trs_mat in trs_mats}
    # for path in Path(gltf_file_directory).rglob("*.gltf"):

    locations = {k: {} for k in boxes.keys()}
    # top key = occlusion box name
    # items =
    #       key: name, value: TRS mat

    item_count = {k: 0 for k in location_table.keys()}
    not_in_bounds = {}
    for path in Path(gltf_file_directory).rglob("*.gltf"):
        if "stream" in str(path):
            # prevents the memory error for the streamobjects in det_sarif_industries
            not_in_bounds[path.stem] = [identity_trs]
            item_count[path.stem] += 1

        else:
            trs_mats = location_table[path.stem]
            for trs_mat in trs_mats:
                if trs_mat == identity_trs:
                    pos = _get_model_center(path)
                else:
                    pos = np.array(trs_mat).reshape((4, 4))[3, :3]

                box = None
                for name, bounds in boxes.items():
                    if trimesh.bounds.contains(bounds, [pos]):
                        box = name
                        break
                if box:
                    if path.stem not in locations[box]:
                        locations[box][path.stem] = []
                    locations[box][path.stem].append(trs_mat)
                    item_count[path.stem] += 1
                else:
                    if path not in not_in_bounds:  # usually the cells/stream
                        not_in_bounds[path.stem] = []
                    not_in_bounds[path.stem].append(trs_mat)
                    item_count[path.stem] += 1

    # assert item_count == {k: len(v) for k, v in location_table.items()}
    # assert len(not_in_bounds) == 0

    # return locations
    out = {}
    for box, contents in locations.items():
        for name, trs_mats in contents.items():
            for mat in trs_mats:
                out[(name, tuple(mat))] = box
    for name, trs_mats in not_in_bounds.items():
        for mat in trs_mats:
            out[(name, mat)] = "OUT"
    return out, boxes


def _get_model_bounds(model_path):
    mesh = trimesh.load(model_path, file_type="gltf", force='mesh')
    return mesh.bounding_box_oriented.bounds
    # c = np.array([(0, 0, 0), (1, 1, 1), (2, 1, 1)])
    # b = trimesh.bounds.contains(a, c)
    #
    # model = trimesh.load_path(model_path)
    # return []


def _get_model_center(model_path):
    mesh = trimesh.load(model_path, file_type="gltf", force='mesh')
    bbox = mesh.bounding_box_oriented
    return np.array(bbox.transform).T[3, :3]
