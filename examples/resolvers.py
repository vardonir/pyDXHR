from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM import DRM
from pyDXHR.DRM.Section.resolver import Reference

# Assumes that you have the PC Director's Cut edition specified in env
bf = Bigfile.from_env()
bf.open()

simple_unit = "det_city_tunnel1.drm"

unit_drm = DRM.from_bigfile(simple_unit, bf)
unit_drm.open()

ref = Reference.from_root(unit_drm)
ref0 = ref.deref(0x0)
ref_linked = ref0.deref(0x4)
rel_count = ref0.access("H", 0x2)
linked_drms = [ref_linked.access_string(0x100 * i, "utf-8") for i in range(rel_count)]

breakpoint()
