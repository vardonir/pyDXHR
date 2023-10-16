""" Utilities for reading the filelist """

from pathlib import Path
from typing import Dict


def crc32bzip2(d: str) -> int:
    """Encodes a string using CRC32-BZIP2"""
    from fastcrc.crc32 import bzip2

    if isinstance(d, str):
        d = d.encode("utf-8")

    return bzip2(d)


def read_filelist(platform_key: str) -> Dict[int, str]:
    """
    Read the provided generic filelist and create a dict
    where the keys are the hashed filenames
    """
    fl = (Path(__file__).parent / "generic.txt").read_text().split()
    return {crc32bzip2(rf"{platform_key}\{i}"): i for i in fl}


if __name__ == "__main__":
    read_filelist("pc-w")
