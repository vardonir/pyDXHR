from pathlib import Path
import pygltflib as gl
from copy import deepcopy


def split_by_occlusion(source_gltf, dest_folder):
    source = gl.GLTF2().load(source_gltf)
    out_dir = Path(dest_folder) / Path(source_gltf).stem

    occlusion_node_table = {}
    mesh_node_table = {}
    for node_idx, node in enumerate(source.nodes):
        if not node.children:  # if a node has no children, then it's a node for a mesh
            node_mesh_name = node.extras["original_name"]
            if node_mesh_name not in mesh_node_table:
                mesh_node_table[node_mesh_name] = []
            mesh_node_table[node_mesh_name].append(node_idx)
        elif "bounds" in node.extras:
            occlusion_node_table[node.name] = node_idx
        elif Path(source_gltf).stem == node.name:
            pass
        else:
            breakpoint()

    for box_name, node_index in occlusion_node_table.items():
        occ_gltf = deepcopy(source)
        occ_node = occ_gltf.nodes[node_index]


        breakpoint()

    breakpoint()


if __name__ == "__main__":
    source_file = r"F:\Projects\pyDXHR\output\unit_gltf\det_city_tunnel1\det_city_tunnel1.gltf"
    dest_dir = r"F:\Projects\pyDXHR\output\occlusion_split"
    split_by_occlusion(source_file, dest_dir)
