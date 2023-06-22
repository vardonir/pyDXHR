"""
Adapted from https://github.com/rrika/dxhr/blob/main/tools/cdcmesh.py
"""
from pathlib import Path
from typing import *
import numpy as np

from pyDXHR.cdcEngine.DRM.Reference import Reference
from pyDXHR.utils import Endian


class CollisionMesh:
    def __init__(self,
                 coll_mesh_ref: Reference,
                 offset: int = 0,
                 endian: Endian = Endian.Little,
                 **kwargs
                 ):
        self.name = kwargs.get("name", f"CollisionMesh_{hex(offset)}")
        # cd0s = coll_mesh_ref.add_offset(offset)
        # self.trs_mat = struct.unpack_from("16f", coll_mesh_ref.section.Data, cd0s.offset)
        # self.trs_mat = cd0s.access_array("f", 16, cd0s.offset)
        # self.trs_mat = np.array(self.trs_mat).reshape((4,4))
        # bbs = coll_mesh_ref.access_array("f", 12, cd0s.offset + 0x40)  # bounding box?
        # bbs = struct.unpack_from("12f", coll_mesh_ref.section.Data, cd0s.offset + 0x40)
        # self._translation = bbs[0:4]

        cd1 = coll_mesh_ref.deref(0x74)
        vtx_ref = cd1.deref(0x20)
        idx_ref = cd1.deref(0x24)

        vertexdata = vtx_ref.section.Data
        indices = idx_ref.section.Data
        indices += b"\0" * ((-len(indices)) % 12)  # pad with zeros so that it's divisible by 12

        self._vertices = np.frombuffer(vertexdata,
                                       dtype=np.dtype(np.float32).newbyteorder(endian.value)).reshape((-1, 3))

        ic = np.frombuffer(indices,
                           dtype=np.dtype(np.uint16).newbyteorder(endian.value)).reshape((-1, 6))
        self._indices = ic[:, 0:3].astype(np.uint32)  # so what's the other BBHHH?

    def to_gltf(self,
                save_to: Optional[str | Path] = None,
                as_bytes: bool = False,
                **kwargs
                ):
        import warnings
        import pygltflib as gltf
        binary_blob = self._vertices.tobytes() + self._indices.flatten().tobytes()

        root = gltf.GLTF2()
        node = gltf.Node(
            name=self.name,
            translation=kwargs.get("translation"),
            scale=kwargs.get("scale"),
            rotation=kwargs.get("rotation"),
            # matrix=self.trs_mat.flatten().tolist(),
        )

        scene = gltf.Scene()
        scene.nodes = [0]
        root.scenes.append(scene)

        root.nodes.append(node)

        mesh = gltf.Mesh(name=self.name)
        node.mesh = 0
        root.meshes.append(mesh)

        vtx_buffer_view = gltf.BufferView(
            buffer=0,
            byteOffset=0,
            byteLength=len(self._vertices.tobytes()),
            target=gltf.ARRAY_BUFFER,
            name=f"{self.name}_Position"
        )

        vtx_accessor = gltf.Accessor(
            componentType=gltf.FLOAT,
            type=gltf.VEC3,
            min=[round(i) - 1 for i in np.min(self._vertices, axis=0).tolist()],
            max=[round(i) + 1 for i in np.max(self._vertices, axis=0).tolist()],
            count=len(self._vertices),
            name=f"{self.name}_Position",
            bufferView=0,
        )

        idx_buffer_view = gltf.BufferView(
            buffer=0,
            byteOffset=len(self._vertices.tobytes()),
            byteLength=len(self._indices.flatten().tobytes()),
            target=gltf.ELEMENT_ARRAY_BUFFER,
            name=f"{self.name}_indices",
        )

        idx_accessor = gltf.Accessor(
            componentType=gltf.UNSIGNED_INT,
            # count=len(self._indices),
            count=self._indices.size,
            type=gltf.SCALAR,
            max=[int(self._indices.max())],
            min=[int(self._indices.min())],
            name=f"{self.name}_indices",
            bufferView=1,
        )

        root.bufferViews.append(vtx_buffer_view)
        root.bufferViews.append(idx_buffer_view)

        root.accessors.append(vtx_accessor)
        root.accessors.append(idx_accessor)

        prim = gltf.Primitive(
            attributes=gltf.Attributes(
                POSITION=0,
            ),
            indices=1,
        )

        mesh.primitives.append(prim)

        buffer = gltf.Buffer()
        buffer.byteLength = len(binary_blob)
        root.buffers.append(buffer)
        root.set_binary_blob(binary_blob)

        if save_to:
            save_to = Path(save_to)
            if save_to.suffix == ".gltf":
                file_destination = save_to
            else:
                file_destination = save_to.parent / (save_to.name + '.gltf')

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=UserWarning)
                root.save(file_destination)

        if as_bytes:
            return b"".join(root.save_to_bytes())
        else:
            return root

