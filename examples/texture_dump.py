from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM import DRM
from pyDXHR.DRM.Section import RenderResource

bf = Bigfile.from_env()
bf.open()

rendermodel = "imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_sarif_office\sarif_office_fire_a\sarif_office_fire_a.drm"  # noqa

drm = DRM.from_bigfile(rendermodel, bf)
drm.open()

rr_list = RenderResource.from_drm(drm)

for rr in rr_list:
    tex = rr.parse_resource_data()
    # tex.to_raw(r"C:\Users\vardo\Documents\pyDXHR\playground\texture")
    tex.to_dds(r"C:\Users\vardo\Documents\pyDXHR\playground\texture")
    # breakpoint()
