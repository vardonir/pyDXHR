from typing import List
import numpy as np
from pyDXHR.DRM.resolver import Reference
from pyDXHR import SectionType


def get_text_references(drm) -> List[Reference]:
    """
    Used by the databases
    TODO: explain me
    """
    root_ref = Reference.from_root(drm)
    header = np.frombuffer(
        root_ref.section.data, dtype=np.dtype(np.uint32).newbyteorder(root_ref.endian)
    )
    length = header[0]
    ids = header[1:]
    assert length == ids.size

    return [
        Reference.from_section_type(
            drm_or_section_list=drm, section_id=s_id, section_type=SectionType.dtpdata
        )
        for s_id in ids
    ]


def get_sections_by_subtype(section_list, subtype):
    """Returns a list of sections with the specified subtype"""
    return [sec for sec in section_list if sec.Header.SectionType == subtype]
