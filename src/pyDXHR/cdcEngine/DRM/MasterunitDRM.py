from typing import *
from pathlib import Path
from tqdm import tqdm, trange

from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM
from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.utils import *


class MasterunitDRM:
    def __init__(self,
                 masterunit_name: str,
                 archive: Archive,
                 **kwargs
                 ):
        self._unit_list: Dict[str, UnitDRM] = {}
        self._archive: Archive = archive
        self._linked_drm_names: List[str] = []
        self._kwargs = kwargs | {"verbose": False}

        self.Name: str = masterunit_name
        self._read_masterunit()

        for linked in self._linked_drm_names:
            filename = linked + ".drm"
            drm_data = self._archive.get_from_filename(filename)

            unit = UnitDRM(**self._kwargs)
            unit.deserialize(drm_data, archive=self._archive, **self._kwargs)
            self._unit_list[linked] = unit

    def _read_masterunit(self):
        name = self.Name if self.Name.endswith("__masterunit.drm") else self.Name + "__masterunit.drm"

        mu_data = self._archive.get_from_filename(name)
        unit = UnitDRM(**self._kwargs)
        unit.deserialize(mu_data, archive=self._archive, **self._kwargs)
        self._unit_list[self.Name] = unit
        self._linked_drm_names = unit.linked_drm()

    def to_gltf(self,
                save_to: str,
                action: str = "overwrite",
                blank_materials: bool = False,
                merge: bool = True
                ):
        from pyDXHR.utils.gltf import merge_multiple

        if Path(save_to).suffix == ".drm":
            save_to = Path(save_to).parent / Path(save_to).stem
        dest = create_directory(save_to=save_to, action=action)

        pbar = tqdm(self._unit_list.items())
        for name, unit in pbar:
            pbar.set_description(f"Generating GLTF for unit {name}")
            unit.to_gltf(save_to=dest / name, blank_materials=blank_materials)

        if merge:
            merge_multiple(
                output_path=dest,
                **self._kwargs,
            )

        if self._kwargs.get("collision", True):
            self._merge_collisions(dest=dest)

    def _merge_collisions(self, dest: str | Path):
        """
        Merge the collision meshes from the different unit DRMs to a single GLTF file -
        TODO: meshes are not positioned correctly
        """

        import pygltflib as gl
        from pyDXHR.utils.gltf.merge import apply_node_transformations

        outfile = Path(dest) / f"CollisionMesh_{self.Name}.gltf"

        # print("Processing collision")
        binary_blob = b''

        merged_file = gl.GLTF2()
        scene = gl.Scene(
            name=f"CollisionMesh_{self.Name}"
        )
        merged_file.scenes.append(scene)
        merged_file.scene = 0

        for name, unit in self._unit_list.items():
            cm = unit.CollisionMesh[0]
            gltf = cm.to_gltf()

            current_node_index = len(merged_file.nodes)
            current_mesh_index = len(merged_file.meshes)
            current_pos_bufferview = len(merged_file.bufferViews)

            assert len(gltf.nodes) == 1
            assert len(gltf.meshes) == 1
            assert len(gltf.meshes[0].primitives) == 1
            assert len(gltf.bufferViews) == 2
            assert len(gltf.accessors) == 2

            node = gltf.nodes[0]
            node.name = f"CollisionMesh_{name}"

            merged_file.nodes.append(node)
            merged_file.nodes[current_node_index].mesh = current_mesh_index

            merged_file.meshes.append(gltf.meshes[0])
            merged_file.meshes[current_mesh_index].primitives[0].attributes = gl.Attributes(
                POSITION=current_pos_bufferview)
            merged_file.meshes[current_mesh_index].primitives[0].indices = current_pos_bufferview + 1

            vtx_bv = gltf.bufferViews[0]
            vtx_bv.name = None

            idx_bv = gltf.bufferViews[1]
            idx_bv.name = None

            vtx_bv.byteOffset = len(binary_blob)
            idx_bv.byteOffset = len(binary_blob) + vtx_bv.byteLength

            merged_file.bufferViews.append(vtx_bv)
            merged_file.bufferViews.append(idx_bv)

            vtx_acc = gltf.accessors[0]
            vtx_acc.name = None

            idx_acc = gltf.accessors[1]
            idx_acc.name = None

            vtx_acc.bufferView = current_pos_bufferview
            idx_acc.bufferView = current_pos_bufferview + 1

            merged_file.accessors.append(vtx_acc)
            merged_file.accessors.append(idx_acc)

            binary_blob += gltf.binary_blob()

        buffer = gl.Buffer()
        buffer.byteLength = len(binary_blob)
        merged_file.buffers.append(buffer)

        top_node = gl.Node(
            name=f"CollisionMesh_{self.Name}"
        )
        top_node.children = list(range(len(merged_file.nodes)))

        top_node = apply_node_transformations(top_node, **self._kwargs)
        scene.nodes.append(len(merged_file.nodes))
        merged_file.nodes.append(top_node)

        merged_file.set_binary_blob(binary_blob)
        merged_file.save(outfile)
