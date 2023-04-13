from pathlib import Path

from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM

pc_base = r"C:\Users\vardo\DXHR_Research\DXHR\BIGFILE.000"
pc_dc = r'C:\Program Files (x86)\GOG Galaxy\Games\Deus Ex HRDC\BIGFILE.000'
ps3_base = r"C:\Users\vardo\DXHR_Research\DXHRPS3\CACHE.000"

pc_arc = Archive()
pc_arc.deserialize_from_file(pc_dc)

sarif_office_globe_path = r"imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_sarif_office\sarif_office_globe\sarif_office_globe.drm"
sarif_building_pelt_a = r"imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_fake_exterior\sarif_building_pelt_a\sarif_building_pelt_a.drm"
pc_data = pc_arc.get_from_filename(sarif_office_globe_path)

pc_drm = DRM()
stat = pc_drm.deserialize(pc_data)

breakpoint()
# ps3_arc = Archive()
# ps3_arc.deserialize_from_file(ps3_base)
#
# drm_path = "weapon_tranquilizergun_upgraded_equip.drm"
# dest = r"C:\Users\vardo\DXHR_Research\pyDXHR\preprocessed\drm_unpacked"
#
# drm_data = ps3_arc.get_from_filename(r"ps3-w\textures.ids")
# texture_dev_file = ps3_arc.get_from_hash(0xB1991FEF)
#
# with open(Path(dest) / "textures.ids", "wb") as f:
#     f.write(texture_dev_file)

