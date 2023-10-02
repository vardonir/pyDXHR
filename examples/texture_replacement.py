file = r"C:\Users\vardo\Documents\pyDXHR\dist\civilian_pritchard.drm"
texture_id = 0x000013ca
replacement_texture = r"C:\Users\vardo\Documents\pyDXHR\dist\textures\000013ca_m.dds"
filename = r"civilian_pritchard.drm"

# get the render resource associated with the texture, because we need the unknowns?
from pyDXHR.DRM import DRM
from pyDXHR.DRM.Section import RenderResource

drm = DRM.from_file(file)
drm.open()


def get_render_resource_for_id(drm_input, rr_id):
    rr_list = RenderResource.from_drm(drm_input)

    for rr in rr_list:
        if rr.section_id == rr_id:
            rr.parse_resource_data()
            return rr


rr_obj = get_render_resource_for_id(drm, texture_id)

# convert dds to pcd9
from pyDXHR.generated.dds import Dds as KaitaiDDS
kt_dds_replacement = KaitaiDDS.from_file(replacement_texture)

pcd9_replace = b"PCD9"
pcd9_replace += kt_dds_replacement.four_cc.value.to_bytes(4, "little")
pcd9_replace += len(kt_dds_replacement.payload).to_bytes(4, "little")
pcd9_replace += kt_dds_replacement.len_mipmaps.to_bytes(4, "little")
pcd9_replace += kt_dds_replacement.width.to_bytes(2, "little")
pcd9_replace += kt_dds_replacement.height.to_bytes(2, "little")

pcd9_replace += rr_obj.unk14.to_bytes(4, "little")
pcd9_replace += rr_obj.unk18.to_bytes(4, "little")
pcd9_replace += kt_dds_replacement.payload

# write the DRM
for sec in drm.sections:
    if sec.header.section_id == texture_id:
        sec.header.len_data = len(pcd9_replace)
        sec.data = pcd9_replace

if len(drm.drm_deps):
    drm_deps = b"\x00".join([d.encode("ascii") for d in drm.drm_deps]) + b"\x00"
else:
    drm_deps = b""

if len(drm.obj_deps):
    obj_deps = b"\x00".join([d.encode("ascii") for d in drm.obj_deps]) + b"\x00"
else:
    obj_deps = b""


repacked_drm = b""
repacked_drm += (0x15).to_bytes(4, "little")
repacked_drm += len(drm_deps).to_bytes(4, "little")
repacked_drm += len(obj_deps).to_bytes(4, "little")
repacked_drm += (0).to_bytes(4, "little")
repacked_drm += (0).to_bytes(4, "little")
repacked_drm += drm.flags.to_bytes(4, "little")
repacked_drm += len(drm.sections).to_bytes(4, "little")
repacked_drm += drm.root_section_index.to_bytes(4, "little")

# section headers
for sec in drm.sections:
    sec_header_repack = b""
    sec_header_repack += sec.header.len_data.to_bytes(4, "little")
    sec_header_repack += sec.header.section_type.value.to_bytes(1, "little")
    sec_header_repack += sec.header.unknown_05.to_bytes(1, "little")
    sec_header_repack += sec.header.unknown_06.to_bytes(2, "little")
    sec_header_repack += sec.header.flags.to_bytes(4, "little")
    sec_header_repack += sec.header.section_id.to_bytes(4, "little")
    sec_header_repack += sec.header.specialization.to_bytes(4, "little")

    repacked_drm += sec_header_repack

# obj dependencies
repacked_drm += obj_deps

# drm dependencies
repacked_drm += drm_deps

# section data
for sec in drm.sections:
    repacked_drm += b"\x00" * ((0x10 - (len(repacked_drm) % 0x10)) % 0x10)
    repacked_drm += sec.reloc_data
    repacked_drm += b"\x00" * ((0x10 - (len(repacked_drm) % 0x10)) % 0x10)
    repacked_drm += sec.data
    repacked_drm += b"\x00" * ((0x10 - (len(repacked_drm) % 0x10)) % 0x10)


# write the bigfile
from pyDXHR.Bigfile import Bigfile, write_from_entries

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
bf.open()

entry = bf.get_entry_from_filename(filename)
entry.byte_data = repacked_drm
entry.uncompressed_size = len(repacked_drm)

new_bf = write_from_entries([entry], bf)

for i in new_bf:
    with open(r"C:\Users\vardo\Documents\pyDXHR\playground\scr\blue_pritchard.000", "wb") as ff:
        ff.write(i)
