from pathlib import Path
from typing import List
from pyDXHR.cdcEngine.Archive import Archive, ArchiveEntry


def repack_bigfile(
        arc: Archive,
        replacement_entries: List[ArchiveEntry],
        file_name: str | Path,
        dest_path: str | Path,
        skip_final_checks: bool = False
) -> None:
    arc.Entries = []
    for entry in replacement_entries:
        arc.append(entry)

    new_bigfile = arc.serialize()

    for idx, byte_data in enumerate(new_bigfile):
        output_file = Path(dest_path) / f"{file_name}.00{idx}"

        print(f"Writing to {Path(output_file).name}")
        with open(output_file, "wb") as f:
            f.write(byte_data)

    if not skip_final_checks:
        print("Final checks")
        new_arc = Archive()
        new_arc.deserialize_from_file(Path(dest_path) / f"{file_name}.000")


