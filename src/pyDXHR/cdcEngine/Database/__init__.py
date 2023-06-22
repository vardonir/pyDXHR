import numpy as np
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.Reference import Reference
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType


class AbstractDatabase(DRM):
    def __init__(self, **kwargs):
        super().__init__()

    def deserialize(self, data: bytes, **kwargs):
        des = super().deserialize(data=data, header_only=False)

        root_ref = Reference.from_drm_root(self)
        header = np.frombuffer(root_ref.section.Data, dtype=np.uint32)
        len_data = header[0]
        data_ids = header[1:]
        assert data_ids.size == len_data

        data_refs = [
            self.lookup_reference(SectionType.DTPData, s_id)
            for s_id in data_ids
        ]

        breakpoint()