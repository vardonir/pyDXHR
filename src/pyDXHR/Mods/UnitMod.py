from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.CompressedDRM import decompress
from pyDXHR.cdcEngine.DRM.Reference import Reference
from tqdm import trange
import struct


def overwrite_data(data: bytes, offset: int, replacement: bytes) -> bytes:
    from io import BytesIO
    data_stream = BytesIO(data)
    data_stream.seek(offset)
    data_stream.write(replacement)
    data_stream.seek(0)
    return data_stream.read()


def replace_object(old_obj_id, new_obj_id, drm: DRM):
    unit_ref = Reference.from_drm_root(drm)
    sub30_ref = unit_ref.deref(0x30)
    obj_ref = sub30_ref.deref(0x18)
    obj_count = sub30_ref.access("I", 0x14)

    endian = obj_ref.section.Header.Endian

    section_bytedata = obj_ref.section.Data
    replacement_bytes = struct.pack(f"{endian.value}H", new_obj_id)

    for i in trange(obj_count, desc=f"Searching for OBJ ID {old_obj_id}"):
        data_offset = 0x30 + obj_ref.offset + i * 0x70
        index, = struct.unpack_from(f"{endian.value}H", section_bytedata, data_offset)
        if index == old_obj_id:
            section_bytedata = overwrite_data(section_bytedata, data_offset, replacement_bytes)

    decompressed_full_data = decompress(drm.ByteData, return_as_bytes=True)
    return overwrite_data(decompressed_full_data, obj_ref.section.PayloadOffset, section_bytedata)


def replace_imf(old_imf_path: str, new_imf_path: str, drm: DRM):
    # TODO: actually put the replacement mesh in there, right now it just deletes the old one
    unit_ref = Reference.from_drm_root(drm)
    sub30_ref = unit_ref.deref(0x30)
    imf_ref = sub30_ref.deref(0xA8)
    imf_count = sub30_ref.access("I", 0xA4)

    section_bytedata = imf_ref.section.Data
    replacement_bytes = new_imf_path.encode("ascii")
    new_str_length_padded = 16 * round(len(replacement_bytes)/16)

    fname_offsets = []
    old_imf_offsets = []
    old_str_length_padded = 0
    for i in trange(imf_count):
        fname_ref = imf_ref.deref(0x4C + i * 0x90)
        if not fname_ref:
            continue

        fname = fname_ref.get_string()
        fname_offsets.append(fname_ref.offset)
        if fname == old_imf_path:
            old_imf_offsets.append(fname_ref.offset)
            old_str_length_padded = 16 * round(len(fname_ref.access_null_terminated())/16)

    if new_str_length_padded > old_str_length_padded:
        raise NotImplementedError
    # fname_start = min(fname_offsets)

    for i in range(old_str_length_padded - new_str_length_padded - 1):
        replacement_bytes += b"\x00"

    for offset in old_imf_offsets:
        section_bytedata = overwrite_data(section_bytedata, offset, replacement_bytes)

    decompressed_full_data = decompress(drm.ByteData, return_as_bytes=True)
    return overwrite_data(decompressed_full_data, imf_ref.section.PayloadOffset, section_bytedata)


def move_object(obj_id, new_pos, drm: DRM):
    pass


def move_imf(imf_path, new_pos, drm: DRM):
    pass


def spawn_object(obj_id, pos, drm: DRM):
    pass
