"""
Unpack bigfile specified in path to a destination folder.
Primarily used by the bigfile_unpack endpoint.
"""

from pathlib import Path
from typing import Optional
from tqdm import tqdm
from pyDXHR.Bigfile import Bigfile
from pyDXHR import FileTypes


def unpack_to_location(
    path_for_000_file: str | Path,
    unpacked_destination: Optional[str | Path] = None,
    skip_unknown: bool = False,
    skip_known: bool = False,
):
    """Unpacks a bigfile to a location"""
    if unpacked_destination is None:
        if Path(path_for_000_file).is_file():
            unpacked_destination = (
                Path(path_for_000_file).parent
                / f"{Path(path_for_000_file).stem}_unpack"
            )
        else:
            unpacked_destination = Path(path_for_000_file)

    if Path(path_for_000_file).is_file():
        assert Path(path_for_000_file).suffix == ".000", "The file must be a .000 file"
        name = Path(path_for_000_file).stem
        dest = Path(unpacked_destination) / f"{name}_unpack"
        unpack_000_file(path_for_000_file, skip_unknown, skip_known, dest, name)
    else:
        unpackable_files = Path(path_for_000_file).glob("*.000")
        for file in unpackable_files:
            name = file.relative_to(path_for_000_file).stem
            dest = Path(unpacked_destination) / f"{name}_unpack"
            unpack_000_file(file, skip_unknown, skip_known, dest, name)


def unpack_000_file(file, skip_unknown, skip_known, dest, name):
    """Unpacks a single .000 file"""
    bf = Bigfile.from_path(file)
    bf.open()

    if not skip_known:
        for (h, loc), entry in tqdm(
            bf.named_entries.items(), desc=f"Unpacking named files from {name}.000"
        ):
            data = bf.read_data(file_hash=h, locale=loc)
            write_file(entry.filename, loc, data, dest, bf.key)

    if not skip_unknown:
        for (h, loc), entry in tqdm(
            bf.unknown_entries.items(), desc=f"Unpacking unknown files from {name}.000"
        ):
            data = bf.read_data(file_hash=h, locale=loc)
            try:
                file_type = FileTypes(data[0:4])
            except ValueError:
                file_type = FileTypes.UNKNOWN
            write_file(
                f"{h:08X}",
                loc,
                data,
                dest,
                bf.key,
                is_unknown=True,
                file_type=file_type,
            )


def write_file(
    file_name,
    locale,
    byte_data,
    destination,
    platform_key,
    is_unknown=False,
    file_type=None,
):
    """
    Writes a file to a destination, given the locale value
    and if it's an unknown. 0xFFFFFFFF is renamed to "default"
    to match the output from Gibbed's unpacker
    """
    if locale == 0xFFFFFFFF:
        if is_unknown:
            dest = (
                Path(destination)
                / "default"
                / "__UNKNOWN"
                / file_type.name.lower()
                / file_name
            )
        else:
            dest = Path(destination) / "default" / platform_key / file_name
        dest.parent.mkdir(exist_ok=True, parents=True)
    else:
        if is_unknown:
            dest = (
                Path(destination)
                / "default"
                / "__UNKNOWN"
                / file_type.name.lower()
                / file_name
            )
        else:
            dest = Path(destination) / f"{locale:08X}" / platform_key / file_name
        dest.parent.mkdir(exist_ok=True, parents=True)

    with open(dest, "wb") as f:
        f.write(byte_data)
