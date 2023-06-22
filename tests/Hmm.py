aug = r"pc-w\jensen_trenchcoat.drm"
natch = r"pc-w\jensen_trenchcoat_notaugmented.drm"

from pyDXHR.utils import crc32bzip2
from pyDXHR.cdcEngine.Archive import Archive, ArchiveEntry

pc_dc_path = r"F:\Games\Deus Ex HRDC\BIGFILE.000"
pc_arc = Archive()
pc_arc.deserialize_from_file(pc_dc_path)

aug_entry = pc_arc.get_from_filename(aug, as_bytes=False)

pc_arc.Entries = []

aug_entry.NameHash = crc32bzip2(natch, dtype=int)
pc_arc.append(aug_entry)

new_bigfile = pc_arc.serialize()

from pathlib import Path

for idx, byte_data in enumerate(new_bigfile):
    output_file = fr"F:\Projects\pyDXHR\output\drm_test\hmm.00{idx}"

    print(f"Writing to {Path(output_file).name}")
    with open(output_file, "wb") as f:
        f.write(byte_data)

print("Final checks")
new_arc = Archive()
new_arc.deserialize_from_file(fr"F:\Projects\pyDXHR\output\drm_test\hmm.000")

breakpoint()
