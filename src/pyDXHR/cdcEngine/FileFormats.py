from enum import Enum

from utils import Endian


class DataType(Enum):
    # references:
    #       https://github.com/gibbed/Gibbed.CrystalDynamics/blob/master/projects/Gibbed.CrystalDynamics.FileFormats/FileExtensions.cs
    #       https://github.com/Gh0stBlade/cdcEngineTools/blob/master/PCD2DDS/PCD.h
    #       https://github.com/rrika/dxhr/blob/main/nb/Filelists.ipynb

    CDRM = b'CDRM', b'CDRM'[::-1]
    USM = b'CRID', b'CRID'[::-1]
    SAM = b"FSB4", b"FSB4"[::-1]
    MUS = b'Mus!', b'Mus!'[::-1]
    ENIC = b"ENIC", b"ENIC"[::-1]
    CINE = b'CRID', b'CRID'[::-1]
    ANIM = b"FxAnim", b"FxAnim"[::-1]
    MUL = 0x44AC0000

    PCD9 = b"PCD9", b"PCD9"[::-1]
    PS3T = b'PS3T', b'PS3T'[::-1]
    MOD = 0x6873654D

    MESH = b'Mesh', b'Mesh'[::-1]

    UNK = b''

    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        for other_value in values[1:]:
            cls._value2member_map_[other_value] = obj
        obj._all_values = values
        return obj


if __name__ == "__main__":
    breakpoint()
