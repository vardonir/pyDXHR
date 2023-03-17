import numpy as np
from pathlib import Path
from utils.types import GameType, archive_prefix


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
