import numpy as np
from pathlib import Path
from enum import Enum


class Endian(Enum):
    Big = ">"
    Little = "<"


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


def crc32bzip2(d: str | bytes, dtype=str):
    from fastcrc.crc32 import bzip2
    if isinstance(d, str):
        d = d.encode("utf-8")

    if dtype == str:
        return hex(bzip2(d))
    else:
        return bzip2(d)


def get_filelist(game: GameType = GameType.BASE, with_hash: bool = True):
    if with_hash:
        out = {}
    else:
        out = []

    with open(Path(__file__).parents[3] / "external" / "filelist_generic.txt", "r") as f:
        for i in f:
            line = archive_prefix(game) + "\\" + i.strip()

            if with_hash:
                out[crc32bzip2(line, dtype=int)] = line
            else:
                out.append(line)

    return out


def byte_swap(data, dtype=np.uint32):
    import numpy as np
    # type_size = np.dtype(dtype).itemsize
    a = np.frombuffer(data, dtype=dtype)
    aa = a.byteswap()
    bb = aa.tobytes()
    return bb


def create_directory(save_to, action: str = "overwrite") -> Path:
    import shutil

    if Path(save_to).is_dir() and action == "overwrite":
        dest = Path(save_to)
        if action == "overwrite":
            shutil.rmtree(dest)
    else:  # Path(save_to).is_file():
        dest = Path(save_to).parent / Path(save_to).stem

    dest.mkdir(parents=True, exist_ok=True)

    return dest


def get_file_size(file_path):
    import os
    return os.stat(file_path).st_size
