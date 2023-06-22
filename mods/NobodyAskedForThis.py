from pathlib import Path
from tqdm import tqdm
from pyDXHR.cdcEngine.Archive import Archive, ArchiveEntry
from pyDXHR.cdcEngine.Sound.MultiplexStream import MultiplexStream
from pyDXHR.utils import crc32bzip2

dialogue_identifier = r"audio\streams\vo\eng"
cinematics_identifier = r"design_database\videos\cinematics\final_cinematics"

pc_dc = r"C:\Users\vardo\DXHR_Research\DXHRDC\BIGFILE.000"
ps3_jap = r"C:\Users\vardo\DXHR_Research\JAP\BIGFILE.000"
generic_filelist = r"C:\Users\vardo\DXHR_Research\pyDXHR\external\filelist_generic.txt"

# with open(generic_filelist, "r") as fl:
#     files_to_be_replaced = [l.strip() for l in fl.readlines() if dialogue_identifier in l]

pc_arc = Archive()
pc_arc.deserialize_from_file(pc_dc)

# clear out the entries in the pc archive - these will be overwritten
pc_arc.Entries = []

ps3_arc = Archive()
ps3_arc.deserialize_from_file(ps3_jap)

# problematic_file_count = 0
# for file in tqdm(files_to_be_replaced, desc="Converting PS3-JAP MUL files"):
#     # get the data from the japanese version
#     ps3_ja_data = ps3_arc.get_from_filename(file, spec=0xffffe020)
#     if ps3_ja_data is None:
#         continue
#
#     # read it as a multiplex stream
#     ps3_ja = MultiplexStream()
#     try:
#         ps3_ja.deserialize(ps3_ja_data)
#     except Exception as e:
#         print(f"Error for file {file}: {e}")
#         problematic_file_count += 1
#     else:
#         new_hash = crc32bzip2("pc-w\\" + file, dtype=int)
#
#         # rebuild it as an archive entry, but swapped
#         new_entry = ps3_ja.to_archive_entry(
#             name_hash=new_hash,
#             locale=0xffffe081,  # turn the locale to english
#             swap=True
#         )
#
#         pc_arc.append(new_entry)
#
# print(f"Processed {len(files_to_be_replaced) - problematic_file_count} out of {len(files_to_be_replaced)}")
# new_bigfile = pc_arc.serialize()
#
# for idx, byte_data in enumerate(new_bigfile):
#     output_file = fr"C:\Users\vardo\DXHR_Research\mods\nobodyaskedforthis.00{idx}"
#
#     print(f"Writing to {Path(output_file).name}")
#     with open(output_file, "wb") as f:
#         f.write(byte_data)
#
# print("Final checks")
# new_arc = Archive()
# new_arc.deserialize_from_file(r"C:\Users\vardo\DXHR_Research\mods\nobodyaskedforthis.000")
#
# breakpoint()


# for the cinematics

with open(generic_filelist, "r") as fl:
    files_to_be_replaced = [l.strip() for l in fl.readlines() if cinematics_identifier in l]

for file in tqdm(files_to_be_replaced, desc="Transferring USM files"):
    ps3_ja_data = ps3_arc.get_from_filename(file)
    if ps3_ja_data is None:
        print(file)
        continue

    arc_entry = ArchiveEntry()
    arc_entry.NameHash = crc32bzip2("pc-w\\" + file, dtype=int)
    arc_entry.Locale = 0xffffffff
    arc_entry.EntryData = ps3_ja_data
    arc_entry.UncompressedSize = len(ps3_ja_data)

    pc_arc.append(arc_entry)

new_bigfile = pc_arc.serialize()

for idx, byte_data in enumerate(new_bigfile):
    output_file = fr"C:\Users\vardo\DXHR_Research\mods\nobodyaskedforthis_cine.00{idx}"

    print(f"Writing to {Path(output_file).name}")
    with open(output_file, "wb") as f:
        f.write(byte_data)

print("Final checks")
new_arc = Archive()
new_arc.deserialize_from_file(r"C:\Users\vardo\DXHR_Research\mods\nobodyaskedforthis_cine.000")

breakpoint()