from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM import DRM
from pyDXHR import SectionType

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PS3)
bf.open()

# drm = "det_sarif_industries.drm"
# drm = r"imf\imf_props\imf_vehicule\chopper_int\chopper_int.drm"
# drm = "television_extralarge.drm"
# drm_name = "s_scn_det1_adamapt_c_det_adam_apt_c.drm"
drm_name = "bee_chopper_a.drm"

drm = DRM.from_bigfile(drm_name, bf)
drm.open()
drm.parse_filenames(bf)

breakpoint()

# out = r"C:\Users\vardo\Documents\pyDXHR\playground"
#
# # for this to work correctly, LongPaths needs to be enabled for win10
# from pathlib import Path
# for sec in drm.sections:
#     if sec.header.section_type == SectionType.generic:
#         continue
#
#     path = Path(out) / drm_name / Path(sec.header.file_name.replace(":", ""))
#     path.parent.mkdir(parents=True, exist_ok=True)
#     with open(path, "wb") as f:
#         f.write(sec.data)
