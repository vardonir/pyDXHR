"""
Enums for file standard types

References:
    Sections:
    https://github.com/rrika/dxhr/blob/main/tools/drmexplore.py
    https://github.com/gibbed/Gibbed.CrystalDynamics/blob/master/projects/Gibbed.DeusEx3.FileFormats/DRM/SectionType.cs

    File types:
    #

    Vertex attributes:
    #

"""

from enum import Enum
from pyDXHR.generated.dxhr_drm import DxhrDrm
from pyDXHR.generated.render_model_buffer import RenderModelBuffer


class FileTypes(Enum):
    """Files extracted from Bigfiles, identified using the first four bytes of the file."""

    CDRM = b"CDRM"
    MUL = 0x0000AC44
    MUS = b"Mus!"
    SAM = b"FSB4"
    USM = b"CRID"
    UNKNOWN = b"?"


VertexAttribute = RenderModelBuffer.VtxSem
SectionType = DxhrDrm.SectionType
SectionSubtype = DxhrDrm.SectionSubtype
