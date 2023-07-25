from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.Mods import UnitMod, repack_bigfile

file = r"pc-w\det_sarif_industries.drm"

arc = Archive()
arc.deserialize_from_env("PC_DC")
data = arc.get_from_filename(file)

drm = DRM()
drm.deserialize(data)

# old_imf_path = r"imf\imf_props\imf_supplies\imf_generic\archives_boxes_a\archives_boxes_a.drm"
old_imf_path = r"imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_sarif_office\sarif_office_globe\sarif_office_globe.drm"
new_imf_path = r"imf\imf_props\imf_supplies\imf_food\box_cereal_a\box_cereal_a.drm"
# new_imf_path = r""
new_data = UnitMod.replace_imf(old_imf_path=old_imf_path, new_imf_path=new_imf_path, drm=drm)

entry_data = arc.get_from_filename(file, spec=0xFFFFFFFF, as_bytes=False)
entry_data.UncompressedSize = len(new_data)
entry_data.EntryData = new_data

repack_bigfile(
    arc=arc,
    replacement_entries=[entry_data],
    file_name="more_cereals",
    dest_path=r"F:\Projects\pyDXHR\playground\unit_obj",
)
