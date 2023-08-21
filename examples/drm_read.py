from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM import DRM

# Assumes that you have the PC Director's Cut edition specified in env
bf = Bigfile.from_env()
bf.open()

drm = DRM.from_bigfile(0xAB0AD4A3, bf)
drm.open()

print("DRM dependencies: ")
for d in drm.drm_deps:
    print(d)

print("Object dependencies: ")
for o in drm.obj_deps:
    print(o)

print(f"Root section index: {'None' if drm.root_section_index == 0xFFFFFFFF else drm.root_section_index}")

print("Sections:")
for sec in drm.sections:
    print(f"{sec.header.section_id:08X}",
          sec.header.section_type.name,
          sec.header.section_subtype.name,
          sec.header.len_data)
