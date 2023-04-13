from typing import Optional
from pathlib import Path
from tqdm import tqdm
from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.Archive import Archive, ArchivePlatform
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.utils import crc32bzip2


def unpack_archive(
        archive: Archive,
        dest_path: str | Path,
        file_list: str | Path,
        skip_unknown: bool = False,
        only_unknown: bool = False,
        decompress_drm: bool = False
):
    dest = Path(dest_path)
    dest.mkdir(parents=True, exist_ok=True)

    files = {}
    archive_prefix = archive.platform.value
    with open(file_list, "r") as fl:
        for l in fl.readlines():
            complete_path = archive_prefix + "\\" + l.strip()
            files[crc32bzip2(complete_path, dtype=int)] = complete_path

    for entry in tqdm(archive.Entries, desc="Processing archive entries"):
        entry_data = archive.get_entry_data(entry)
        file_dest = dest / f"{entry.Locale:x}".rjust(8, '0').upper()

        if entry.NameHash in files:
            file_dest = file_dest / Path(files[entry.NameHash]).parent
            file_dest.mkdir(parents=True, exist_ok=True)

            file_dest = file_dest / Path(files[entry.NameHash]).name
            with open(file_dest, "wb") as f:
                f.write(entry_data)

        else:
            file_dest = file_dest / "UNKNOWN"
            file_dest.mkdir(parents=True, exist_ok=True)

            file_dest = file_dest / f"{entry.NameHash:x}".rjust(8, '0').upper()
            with open(file_dest, "wb") as f:
                f.write(entry_data)
