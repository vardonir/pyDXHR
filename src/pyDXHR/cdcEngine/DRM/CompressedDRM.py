import struct
import numpy as np
import zlib
from typing import List

from pyDXHR.utils import Endian

Magic = 0x4344524D


def decompress(data: bytes, header_only: bool = False) -> List[bytes]:
    magic, = struct.unpack_from(">L", data, 0)
    if magic != Magic:
        raise Exception

    le_version, = struct.unpack_from("<L", data, 4)
    be_version, = struct.unpack_from(">L", data, 4)
    if le_version != 0 and le_version != 2 and be_version != 2:
        raise Exception

    if le_version == 0:
        raise NotImplementedError
        # count, = struct.unpack_from("<L", data, 8)
        # if count > 0x7FFFFF:
        #     endian = Endian.Big
        #     count, = struct.unpack_from(">L", data, 8)
        # else:
        #     endian = Endian.Little

        # padding = (uint)(basePosition + 16 + (count * 8));
        # padding = padding.Align(16) - padding;
    else:
        endian = Endian.Little if le_version == 2 else Endian.Big
        count, = struct.unpack_from(f"{endian.value}L", data, 8)
        padding, = struct.unpack_from(f"{endian.value}L", data, 12)

    start_of_data = 16 + (count * 8) + padding
    block_sizes = np.frombuffer(data,
                                dtype=np.dtype(np.uint32).newbyteorder(endian.value),
                                count=2 * count,
                                offset=16).reshape((count, 2))

    blocks = []
    cursor = start_of_data
    for idx, i in enumerate(block_sizes):
        if header_only and idx == 1:
            break

        cursor = (cursor + 0x0F) & (~0x0F)

        unpacked_size = i[0] >> 8
        packed_size = i[1]
        compression_type = i[0] & 0xFF

        block_data = data[cursor: cursor+packed_size]
        cursor += packed_size.item()

        if compression_type == 1:
            if unpacked_size != packed_size:
                raise Exception("Uncompressed data size mismatch")
            blocks.append(block_data)
        elif compression_type == 2:
            decompressed_data = zlib.decompress(block_data)
            blocks.append(decompressed_data)
            assert len(decompressed_data) == unpacked_size
        else:
            raise Exception("Unknown compression type")

    return blocks


def rebuild_aligned(byte_list: List[bytes]) -> bytes:
    for idx, blk in enumerate(byte_list):
        padding = (16 - len(blk)) & 0xF
        byte_list[idx] = byte_list[idx] + (b"\0" * padding)

    return b"".join(byte_list)
