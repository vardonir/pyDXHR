def write_from_entries(entries, source_bigfile):
    from pyDXHR.Bigfile import Bigfile
    import struct

    out_data = b""
    out_data += struct.pack(f"{source_bigfile.endian}L", source_bigfile.alignment)
    if isinstance(source_bigfile.platform, Bigfile.Platform):
        platform_as_bytes = bytes(source_bigfile.key, "ascii")
    else:
        raise Exception

    platform_padding_size = 64 - len(out_data)
    out_data += platform_as_bytes + b"\x00" * platform_padding_size

    out_data += struct.pack(f"{source_bigfile.endian}L", len(entries))

    est_header_size = 4 + 64 + 4 + (4 * (len(entries))) + (16 * len(entries))
    est_header_size += ((0x800 - est_header_size) % 0x800) % 0x800

    # the entries need to be sorted by size and hash
    replacement_entries = sorted(
        sorted(entries, key=lambda x: x.uncompressed_size), key=lambda y: y.name_hash
    )

    archive_data = _repack_archive_entries(
        header_size=est_header_size,
        data_alignment=source_bigfile.alignment,
        entries=replacement_entries,
    )

    # pack in the name hashes
    for entry in replacement_entries:
        out_data += struct.pack(f"{source_bigfile.endian}L", entry.name_hash)

    # pack in the entry data
    for entry in replacement_entries:
        out_data += struct.pack(f"{source_bigfile.endian}L", entry.uncompressed_size)
        out_data += struct.pack(f"{source_bigfile.endian}L", entry.offset)
        out_data += struct.pack(f"{source_bigfile.endian}L", entry.locale)
        out_data += struct.pack(f"{source_bigfile.endian}L", entry.compressed_size)

    # pad header with zeroes
    len_diff = ((0x800 - len(out_data)) % 0x800) % 0x800
    out_data += b"\x00" * len_diff

    # add the first archive data
    out_data += archive_data[0]

    # pad it again with zeroes
    len_diff = ((0x800 - len(out_data)) % 0x800) % 0x800
    out_data += b"\x00" * len_diff

    if len(archive_data) > 1:
        out = [out_data]
        out.extend(archive_data[1:])
        return out
    else:
        return [out_data]


def _repack_archive_entries(header_size, data_alignment, entries):
    out_data_list = [b""]

    max_blocks_per_file = data_alignment // 2048

    current_bigfile_index = 0
    global_pos = 0
    pos = header_size // 0x800

    for entry_idx, entry in enumerate(entries):
        if entry.byte_data is None:
            raise Exception
        if entry.uncompressed_size == 0:
            raise Exception
        if entry.compressed_size:
            pass

        block_count = (len(entry.byte_data) + 0x800 - 1) // 0x800
        if block_count > max_blocks_per_file:
            block_count = max_blocks_per_file

        if pos + block_count > max_blocks_per_file:
            pos = 0
            global_pos += max_blocks_per_file

            len_diff = (
                (0x800 - len(out_data_list[current_bigfile_index])) % 0x800
            ) % 0x800
            out_data_list[current_bigfile_index] += b"\x00" * len_diff

            out_data_list.append(b"")
            current_bigfile_index += 1

        # add the entry
        entry.offset = global_pos + pos
        out_data_list[current_bigfile_index] += entry.byte_data

        # pad this entry with zeros
        len_diff = ((0x800 - len(out_data_list[current_bigfile_index])) % 0x800) % 0x800
        out_data_list[current_bigfile_index] += b"\x00" * len_diff
        pos += block_count

    return out_data_list
