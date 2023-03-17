from enum import Enum


class GameType(Enum):
    BASE = "BASE"
    TML = "TML"
    DC = "DC"
    BASE_PS3 = "BASE_PS3"
    BASE_XENON = "BASE_XENON"
    JAP_PS3 = "JAP_PS3"


def archive_prefix(game: GameType):
    match game:
        case GameType.BASE | GameType.TML | GameType.DC:
            return "pc-w"
        case GameType.BASE_PS3:
            return "ps3-w"
        case GameType.BASE_XENON:
            return "xenon-w"
        case GameType.JAP_PS3:
            return "ps3-jap"
        case _:
            raise KeyError


class TextureFormat(Enum):
    A8R8G8B8 = 0x00000015.to_bytes(4, "little")
    DXT1 = 0x31545844.to_bytes(4, "little")
    DXT3 = 0x33545844.to_bytes(4, "little")
    DXT5 = 0x35545844.to_bytes(4, "little")

    @classmethod
    def from_texture_section_data(cls, data):
        if data[0:4] == b"\x50\x53\x33\x54":
            # mostly guessing for dxt3 and a8r8g8b8
            match data[12:13]:
                case b"\x85":
                    return cls.A8R8G8B8
                case b"\x86":
                    return cls.DXT1
                case b"\xA5":
                    return cls.DXT3
                case b"\x88":
                    return cls.DXT5
                case _:
                    raise Exception
        elif data[0:4] in (b"\x39\x44\x43\x50", b"\x50\x43\x44\x39"):
            return cls(data[4:8])
        else:
            raise Exception
