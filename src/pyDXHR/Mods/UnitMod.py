from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.CompressedDRM import decompress
from pyDXHR.cdcEngine.DRM.Reference import Reference
from tqdm import trange
import struct
from io import BytesIO


def replace_object(old_obj_id, new_obj_id, drm: DRM, byte_data: bytes):
    unit_ref = Reference.from_drm_root(drm)
    sub30_ref = unit_ref.deref(0x30)
    obj_ref = sub30_ref.deref(0x18)
    obj_count = sub30_ref.access("I", 0x14)

    endian = obj_ref.section.Header.Endian

    section_bytedata = obj_ref.section.Data
    replacement_bytes = struct.pack(f"{endian.value}H", new_obj_id)
    section_bytedata_stream = BytesIO(section_bytedata)

    for i in trange(obj_count, desc=f"Searching for OBJ ID {old_obj_id}"):
        data_offset = 0x30 + obj_ref.offset + i * 0x70
        index, = struct.unpack_from(f"{endian.value}H", section_bytedata, data_offset)
        if index == old_obj_id:
            section_bytedata_stream.seek(data_offset)
            section_bytedata_stream.write(replacement_bytes)

    section_bytedata_stream.seek(0)
    new_section_bytedata = section_bytedata_stream.read()

    decompressed_full_data = decompress(byte_data, return_as_bytes=True)
    decompressed_full_data_stream = BytesIO(decompressed_full_data)
    decompressed_full_data_stream.seek(obj_ref.section.PayloadOffset)
    decompressed_full_data_stream.write(new_section_bytedata)

    decompressed_full_data_stream.seek(0)
    return decompressed_full_data_stream.read()


def replace_imf(old_imf_path, new_imf_path, drm: DRM):
    pass


def move_object(obj_id, new_pos, drm: DRM):
    pass


def move_imf(imf_path, new_pos, drm: DRM):
    pass


def spawn_object(obj_id, pos, drm: DRM):
    pass
