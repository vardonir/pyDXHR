from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import CompressedDRM

arc = Archive()
arc.deserialize_from_env()

cdrm_bytes = arc.get_from_filename("det_city_sarif.drm")
decompressed = CompressedDRM.decompress(cdrm_bytes, return_as_bytes=True)
