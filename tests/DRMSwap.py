interactive = r"pc-w\s_scn_det_sarif_industries_sarifcomputerinteractive_det_sarif_industries.drm"
noninteractive = r"pc-w\s_scn_det_sarif_industries_sarifcomputernoninter_det_sarif_industries.drm"

from pyDXHR.utils import crc32bzip2
from pyDXHR.cdcEngine.Archive import Archive, ArchiveEntry

# int_crc = crc32bzip2(interactive)
# nint_crc = crc32bzip2(noninteractive)

pc_dc_path = r"F:\Games\Deus Ex HRDC\BIGFILE.000"
pc_arc = Archive()
pc_arc.deserialize_from_file(pc_dc_path)

interactive_data = pc_arc.get_from_filename(interactive, spec=0xFFFFFFFF, as_bytes=False)

pc_arc.Entries = []

interactive_data.NameHash = crc32bzip2(noninteractive, dtype=int)
# arc_entry = ArchiveEntry()
# arc_entry.NameHash = crc32bzip2(noninteractive, dtype=int)
# arc_entry.Locale = 0xFFFFFFFF
# arc_entry.EntryData = interactive_data.EntryData
# arc_entry.UncompressedSize = len(interactive_data.EntryData)

pc_arc.append(interactive_data)

new_bigfile = pc_arc.serialize()

from pathlib import Path

for idx, byte_data in enumerate(new_bigfile):
    output_file = fr"F:\Projects\pyDXHR\output\drm_test\sarif_hack.00{idx}"

    print(f"Writing to {Path(output_file).name}")
    with open(output_file, "wb") as f:
        f.write(byte_data)

print("Final checks")
new_arc = Archive()
new_arc.deserialize_from_file(fr"F:\Projects\pyDXHR\output\drm_test\sarif_hack.000")

breakpoint()
