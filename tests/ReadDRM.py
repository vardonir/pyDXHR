from cdcEngine.Sections.ShaderLib import ShaderLib, from_drm
from cdcEngine.Sections import RenderMesh, RenderResource
from cdcEngine.Sections.Material import Material
from cdcEngine.DRM.Reference import *
from cdcEngine.DRM.Resolver import *
from cdcEngine.DRM.SectionTypes import SectionType
from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pathlib import Path

# comparison with other versions
arc = Archive()
arc.deserialize_from_env()

# arc = Archive()
# arc.deserialize_from_file(r"F:\DXHRDCWII\bigfile-wiiu.000")

# arc = Archive()
# arc.deserialize_from_file(r"F:\DXHRPS3\CACHE.000")

# per-file comparison
# renderterrain
# data = arc.get_from_filename("streamgroups/det_city_tunnel1_tunel.drm")

# simple object
# data = arc.get_from_filename("alc_vodka_bottle_a.drm")

# imf - has transparency
# data = arc.get_from_filename(r"imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_sarif_office\sarif_office_fire_a\sarif_office_fire_a.drm")

# imf - has emission
# data = arc.get_from_filename(r"imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_sarif_office\sarif_office_globe\sarif_office_globe.drm")

# some interesting drms...
# data = arc.get_from_filename(r"con_009_sari.drm")
# data = arc.get_from_filename(r"occupation_bedsleep.drm")
data = arc.get_from_filename(r"alarm_dispatcher.drm")

drm = DRM()
drm.deserialize(data, archive=arc)
root_ref = Reference.from_drm_root(drm)


# # notes for "con_xxx_xxxx.drm"
# root_ref = Reference.from_drm_root(drm)
#
# # seems like an ID of some kind
# unk1 = root_ref.deref(8).access("L")
# # con_009_sari - 54907
#
# # references to mostly scripts
# unk2 = root_ref.deref(0)














# rm = RenderMesh.deserialize_drm(drm)
# rm0 = list(rm)[0]
# rm0.to_gltf()

breakpoint()

# out = {}
# for dep in drm.Header.DRMDependencies:
#     t_drm = DRM()
#     t_drm.deserialize(arc.get_from_filename(dep))
#
#     for sec in t_drm.Sections:
#         if sec.Header.SectionType == SectionType.ShaderLib:
#             out[hex(sec.Header.SecId)] = sec
#
# a = ShaderLib(section=out.get("0x1d40")).bytecode_chunks[0]
# aa = a.d3d1x_run()

#
# for s in drm.Sections:
#     if s.Header.SectionType == SectionType.Material:
#         m = Material(section=s)
#         m.debug_print()
#
#         m.from_drm(drm=drm, arc=arc)
#
#         breakpoint()

# scaleform database
# data = arc.get_from_filename(r"globalscaleformdatabase.drm")

# with open(r"C:\Users\vardo\DXHR_Research\pyDXHR_public\playground\debug_menu\globalscaleformdatabase_ps3.drm", "wb") as f:
#     f.write(data)

# shaderlib
# with open(r"C:\Users\vardo\DXHR_Research\pyDXHR_public\external\filelist_generic.txt", "r") as f:
#     for l in f:
#         line = l.strip()
#
#         if "shaderlibs" in line:
#             if "dx9" in line:
#                 st = Path(line).stem
#                 # if not st.startswith("chr_"):
#                 #     continue
#
#                 # data = arc.get_from_filename(r"shaderlibs\dn_3bd1408a29369b91_dx11.drm")
#                 data = arc.get_from_filename(line)
#                 if data is None:
#                     continue
#
#                 print(line)
#
#                 drm = DRM()
#                 drm.deserialize(data)
#
#                 sls = from_drm(drm)
#
#                 # for sec in drm.Sections:
#                 #     ShaderLib(section=sec)

# data = arc.get_from_filename(r"shaderlibs\2d_2c995167ccebe443_dx11.drm")
# drm = DRM()
# drm.deserialize(data)
# sls = from_drm(drm)
# for sec in drm.Sections:
#     ShaderLib(section=sec)

breakpoint()
