"""
References:
    https://github.com/rrika/dxhr/blob/main/tools/drmexplore.py
    https://github.com/gibbed/Gibbed.CrystalDynamics/blob/master/projects/Gibbed.DeusEx3.FileFormats/DRM/SectionType.cs

Notes:
    Can't say I've seen DXHR use type 03/04, but some code for one of the Tomb Raider games call them PushBuffer
"""
from enum import IntEnum


class SectionType(IntEnum):
    Generic = 0
    Empty = 1
    Animation = 2
    Unknown03 = 3  # PushBuffer?
    Unknown04 = 4  # PushBuffer
    RenderResource = 5
    FMODSoundBank = 6  # or Wave
    DTPData = 7
    Script = 8
    ShaderLib = 9
    Material = 10
    Object = 11
    RenderMesh = 12
    CollisionMesh = 13
    StreamGroupList = 14
    AnyType = 15

    UnknownSectionType = -1


class SectionSubtype(IntEnum):
    Generic = 0  # I'm guessing
    Texture = 5
    Unknown11 = 11
    Sound = 13
    Unknown16 = 16
    Unknown17 = 17
    Unknown18 = 18  # ps3 - material subtype?
    Unknown19 = 19
    Unknown20 = 20  # ps3 - DTPData .dat
    Unknown21 = 21
    RenderTerrain = 24
    Unknown25 = 25  # seems to come up in ps3 as DTPData - "datfxi"
    RenderModel = 26
    RenderModelBuffer = 27  # used in ps3
    Unknown28 = 28
    Unknown30 = 30  # Object?
    Unknown32 = 32
    Unknown34 = 34
    Unknown36 = 36  # mtl_a/b
    SmartScript = 40
    Scaleform = 41
    Conversation = 42
    Unknown48 = 48  # ft1 = 12, ft2 = 48: scene
    CameraShake = 50
    Unknown52 = 52  # ft1 = 12, ft2 = 52: model

    UnknownSectionSubtype = -1
