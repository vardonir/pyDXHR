"""
Adapted from https://github.com/gibbed/Gibbed.CrystalDynamics/blob/master/projects/Gibbed.CrystalDynamics.FileFormats/ArchiveLocale.cs
"""

from enum import IntEnum


class ArchiveLocale(IntEnum):
    NONE = 0
    English = 1 << 0
    French = 1 << 1
    German = 1 << 2
    Italian = 1 << 3
    Spanish = 1 << 4
    Japanese = 1 << 5
    Portuguese = 1 << 6
    Polish = 1 << 7
    EnglishUnitedKingdom = 1 << 8
    Russian = 1 << 9
    Czech = 1 << 10
    Dutch = 1 << 11
    Hungarian = 1 << 12
    Arabic = 1 << 13
    Korean = 1 << 14
    Chinese = 1 << 15
    Default = 0xFFFFFFFF


def get_locale(value: int) -> ArchiveLocale:
    get = [i for i in ArchiveLocale if i & value == value]
    if len(get) == 1:
        return get[0]
    else:
        return ArchiveLocale.NONE


    # @classmethod
    # def __init__(cls, value):
    #     # [k for k, v in cls.__dict__.items() if isinstance(v, int)]
    #     for k, v in cls.__dict__.items():
    #         if isinstance(v, int):
    #             if v & value == value:
    #                 a = k

        # breakpoint()


loc = get_locale(4294959120)

breakpoint()
