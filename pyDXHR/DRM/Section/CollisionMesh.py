import numpy as np
from typing import List, Optional

from pyDXHR.export.mesh import MeshData
from pyDXHR.DRM.resolver import Reference
from pyDXHR import VertexAttribute


class CollisionMesh:
    def __init__(self):
        self.reference: Optional[Reference] = None
        self.endian: str = "<"
        self.section_id: int = -1
        self.resource_name: Optional[str] = None

    @classmethod
    def from_reference(cls, ref: Reference):
        obj = cls()
        obj.reference = ref
        obj.section_id = ref.section.header.section_id
        obj.endian = ref.section.header.endian
        return obj

    def read(self):
        return self.parse_mesh_data()

    def parse_mesh_data(self):
        vtx_ref = self.reference.deref(0x20)
        idx_ref = self.reference.deref(0x24)

        vertexdata = vtx_ref.section.data
        indices = idx_ref.section.data
        indices += b"\0" * (
            (-len(indices)) % 12
        )  # pad with zeros so that it's divisible by 12

        vertices = np.frombuffer(
            vertexdata, dtype=np.dtype(np.float32).newbyteorder(self.endian)
        ).reshape(
            (-1, 3)
        )  # noqa

        ic = np.frombuffer(
            indices, dtype=np.dtype(np.uint16).newbyteorder(self.endian)
        ).reshape(
            (-1, 6)
        )  # noqa
        indices = ic[:, 0:3].astype(np.uint32)

        return MeshData(
            vertex_buffers={0: {VertexAttribute.position: vertices}},
            mesh_prim_indexed={0: [(0, indices)]},
            material_list=[0],
        )


def from_drm(drm) -> List[CollisionMesh]:
    unit_ref = Reference.from_root(drm)
    sub0_ref = unit_ref.deref(0)
    coll_mesh_ref = sub0_ref.deref(0x18)

    coll_mesh_list = []
    if coll_mesh_ref:
        coll_count = sub0_ref.access("I", 0x14)

        cd1 = coll_mesh_ref.deref(0x74)
        if cd1:
            coll_mesh_list.append(CollisionMesh.from_reference(cd1))

    return coll_mesh_list
