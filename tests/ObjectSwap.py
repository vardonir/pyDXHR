from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.Mods import UnitMod

# pick a unit where you want to swap stuff in
file = "pc-w\det_sarif_industries.drm"

# load the data
arc = Archive()
arc.deserialize_from_env("PC_DC")
data = arc.get_from_filename(file)

# read it as a DRM. this way, i can skip ahead to reading just the reference to the objects
drm = DRM()
drm.deserialize(data)

from pyDXHR.cdcEngine.DRM.CompressedDRM import decompress
decomp = decompress(data, return_as_bytes=True)

# for example, I want to replace all ebooks in the sarif HQ with praxis kits
new_data = UnitMod.replace_object(old_obj_id=139, new_obj_id=226, drm=drm, byte_data=data)
# 136,139,ebook_a
# 223,226,praxiskit

entry_data = arc.get_from_filename(file, spec=0xFFFFFFFF, as_bytes=False)
arc.Entries = []
entry_data.UncompressedSize = len(new_data)
entry_data.EntryData = new_data
arc.append(entry_data)
new_bigfile = arc.serialize()

from pathlib import Path

for idx, byte_data in enumerate(new_bigfile):
    output_file = fr"F:\Projects\pyDXHR\playground\unit_obj\sarifhq_praxis.00{idx}"

    print(f"Writing to {Path(output_file).name}")
    with open(output_file, "wb") as f:
        f.write(byte_data)

print("Final checks")
new_arc = Archive()
new_arc.deserialize_from_file(fr"F:\Projects\pyDXHR\playground\unit_obj\sarifhq_praxis.000")


# imf\imf_props\imf_supplies\imf_food\box_cereal_a\box_cereal_a.drm

