from pathlib import Path
from tqdm import tqdm
from pyDXHR.cdcEngine.Archive import Archive
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
            if only_unknown:
                continue
            file_dest = file_dest / Path(files[entry.NameHash]).parent
            file_dest.mkdir(parents=True, exist_ok=True)

            file_dest = file_dest / Path(files[entry.NameHash]).name
            with open(file_dest, "wb") as f:
                f.write(entry_data)

        else:
            if skip_unknown:
                continue

            if entry_data[0:4] == b"CDRM":
                file_dest = file_dest / "UNKNOWN" / "DRM"
            elif entry_data[0:4] == b'\x00\x00\xacD':
                # TODO
                file_dest = file_dest / "UNKNOWN" / "X1"
            elif entry_data[0:4] == b'CRID':
                file_dest = file_dest / "UNKNOWN" / "CRID"
            else:
                file_dest = file_dest / "UNKNOWN" / "X2"

            file_dest = file_dest / "UNKNOWN"
            file_dest.mkdir(parents=True, exist_ok=True)

            file_dest = file_dest / f"{entry.NameHash:x}".rjust(8, '0').upper()
            with open(file_dest, "wb") as f:
                f.write(entry_data)
