from pathlib import Path
from pyDXHR.DRM import DRM
from pyDXHR.DRM.Section import RenderResource
from pyDXHR.Bigfile import Bigfile
from pyDXHR.export import gltf

replacement_texture = r"C:\Users\vardo\Documents\pyDXHR\playground\scr\4k.dds"
destination = r"C:\Users\vardo\Documents\pyDXHR\playground\size_limit_experiment"
# filename = r"imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_atrium\atrium_column_small_a\atrium_column_small_a.drm"  # noqa
filename = r"streamgroups\det_adam_apt_c_all.drm"

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
bf.open()

drm = DRM.from_bigfile(filename, bf)
drm.open()

# if the textures dir didnt exist yet, use this to generate it
# gltf.from_drm(drm,
#               save_to=Path(destination) / "output.gltf",
#               scale=0.002, z_up=True
#               )

rr_list = RenderResource.from_drm(drm)

textures = Path(destination) / "textures"
texs = list(textures.glob("*.dds"))
# assert len(list(texs)) == len(rr_list)

for rr in rr_list:
    rr.parse_resource_data()
    for tex in texs:
        if int(tex.stem, 16) == rr.section_id:
            # breakpoint()

            # convert dds to pcd9
            from pyDXHR.generated.dds import Dds as KaitaiDDS
            kt_dds_replacement = KaitaiDDS.from_file(replacement_texture)

            pcd9_replace = b"PCD9"
            pcd9_replace += kt_dds_replacement.four_cc.value.to_bytes(4, "little")
            pcd9_replace += len(kt_dds_replacement.payload).to_bytes(4, "little")
            pcd9_replace += kt_dds_replacement.len_mipmaps.to_bytes(4, "little")
            pcd9_replace += kt_dds_replacement.width.to_bytes(2, "little")
            pcd9_replace += kt_dds_replacement.height.to_bytes(2, "little")

            pcd9_replace += rr.unk14.to_bytes(4, "little")
            pcd9_replace += rr.unk18.to_bytes(4, "little")
            pcd9_replace += kt_dds_replacement.payload

            # write the DRM section
            for sec in drm.sections:
                if sec.header.section_id == rr.section_id:
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
    with open(r"C:\Users\vardo\Documents\pyDXHR\playground\scr\4k.000", "wb") as ff:
        ff.write(i)
