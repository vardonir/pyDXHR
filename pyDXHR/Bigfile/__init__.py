"""
Bigfile class
- can read bigfiles specified from the env file, from a specific path.
- can write a new bigfile from a list of BigfileEntry objects
"""

from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Tuple

import numpy as np

from pyDXHR.Bigfile.filelist import read_filelist, crc32bzip2
from pyDXHR.Bigfile.read_header import BigfileHeader
from pyDXHR.Bigfile.read_entries import BigfileEntry
from pyDXHR.Bigfile.pack import write_from_entries


write_new_bigfile = write_from_entries


class BigfileError(Exception):
    """raised for generic bigfile-related errors"""

    pass


class Bigfile:
    """DXHR bigfile"""

    class Version(Enum):
        """game version"""

        # these do not match the platform keys in the file,
        # since the options are either -jap for the
        # japanese version and -w for the rest.
        BASE = "base"
        MISSING_LINK = "tml"
        DIRECTORS_CUT = "dc"
        JAPAN = "japan"
        BETA = "beta"

    class Platform(Enum):
        """game platform"""

        # these match the platform keys in the file
        PC = "pc"
        XBOX360 = "xenon"
        PS3 = "ps3"
        WII_U = "wiiu"

    def __init__(self) -> None:
        self.platform: Optional[Bigfile.Platform] = None
        self.version: Optional[Bigfile.Version] = None

        # this is important for the base/console versions -
        self.unpack_from: str = "bigfile"

        self._path: Optional[Path] = None
        self._is_opened: bool = False
        self._platform_key: str = ""
        self._data_alignment: int = -1
        self._endian: str = "<"

        self.named_entries: Dict[Tuple[int, int], BigfileEntry] = {}
        self.unknown_entries: Dict[Tuple[int, int], BigfileEntry] = {}

    @property
    def key(self):
        return self._platform_key

    @property
    def alignment(self):
        return self._data_alignment

    @property
    def endian(self):
        return self._endian

    def open(self):
        file_path = self._path if self._path else Path(self._get_path())
        file_path = Path(file_path)
        bh = BigfileHeader.from_file(file_path / f"{self.unpack_from}.000")

        self._platform_key = bh.platform_key
        self._data_alignment = bh.data_alignment

        # check if the platform key in the bigfile is valid
        # .lower() is added to accommodate the base game's patch files -
        # their platform key is "PC-W" in caps
        if self.platform is not None:
            # intended for loading from .env
            if bh.platform_key.split("-")[0].lower() != self.platform.value:
                raise BigfileError(
                    f"Invalid platform key in bigfile, found {bh.platform_key}"
                )

            if (
                bh.platform_key.split("-")[1].lower() == "w"
                and self.version == Bigfile.Version.JAPAN
            ):
                raise BigfileError
            if (
                bh.platform_key.split("-")[1].lower() == "jap"
                and self.version != Bigfile.Version.JAPAN
            ):
                raise BigfileError
        else:
            # intended for loading from file/path, specifically the unpacker
            # if you're using the unpacker, then these don't really
            # matter to you, but if you're using pyDXHR as a module,
            # you'll need to specify the version in the factory constructor/
            # anyway, platform can be auto-detected, so...
            self.platform = Bigfile.Platform(bh.platform_key.split("-")[0].lower())

        if self.platform == Bigfile.Platform.PC:
            self._endian = "<"
        else:
            self._endian = ">"

        file_list_dict = read_filelist(bh.platform_key.lower())
        # read the entries
        for e, h in zip(bh.file_headers, bh.file_hashes):
            archive_entry = BigfileEntry()
            archive_entry.name_hash = h
            archive_entry.locale = e.locale
            archive_entry.offset = e.offset
            archive_entry.compressed_size = e.len_compressed
            archive_entry.uncompressed_size = e.len_uncompressed

            try:
                archive_entry.filename = file_list_dict[h]
            except KeyError:
                if (h, e.locale) in self.unknown_entries:
                    raise KeyError
                self.unknown_entries[(h, e.locale)] = archive_entry
            else:
                if (h, e.locale) in self.named_entries:
                    raise KeyError
                self.named_entries[(h, e.locale)] = archive_entry

        self._is_opened = True

    def get_entry_from_filename(
        self, filename: str, locale: int = 0xFFFFFFFF
    ) -> BigfileEntry:
        if not self._is_opened:
            self.open()

        if not filename.startswith(self._platform_key):
            filename = self._platform_key + "\\" + filename

        file_hash = crc32bzip2(filename)
        if (file_hash, locale) in self.named_entries:
            entry = self.named_entries[(file_hash, locale)]
        elif (file_hash, locale) in self.unknown_entries:
            entry = self.unknown_entries[(file_hash, locale)]
        else:
            raise KeyError
        return entry

    def read_data(self, file_hash: int, locale: int = 0xFFFFFFFF):
        if not self._is_opened:
            self.open()

        if (file_hash, locale) in self.named_entries:
            entry = self.named_entries[(file_hash, locale)]
        elif (file_hash, locale) in self.unknown_entries:
            entry = self.unknown_entries[(file_hash, locale)]
        else:
            raise KeyError

        bigfile_index = np.uint32(
            (entry.offset * 0x800) / np.uint64(self._data_alignment)
        )
        bigfile_offset = np.uint32(
            (entry.offset * 0x800) % np.uint64(self._data_alignment)
        )

        with open(self._path_by_index(bigfile_index), "rb") as bigfile:
            bigfile.seek(bigfile_offset)
            data = bigfile.read(entry.uncompressed_size)

        return data

    def _path_by_index(self, index: int):
        """Get the i-th Bigfile in the folder"""
        return Path(self._path) / f"{self.unpack_from}.{index:03}"

    def read_data_by_name(self, filename: str, locale: int = 0xFFFFFFFF):
        if not self._is_opened:
            self.open()

        if not filename.startswith(self._platform_key):
            filename = self._platform_key + "\\" + filename

        file_hash = crc32bzip2(filename)
        return self.read_data(file_hash, locale)

    def read(self, filename_or_hash: str | int, locale: int = 0xFFFFFFFF):
        if isinstance(filename_or_hash, str):
            return self.read_data_by_name(filename_or_hash, locale)
        elif isinstance(filename_or_hash, int):
            return self.read_data(filename_or_hash, locale)
        else:
            raise TypeError

    def _get_path(self):
        from dotenv import load_dotenv

        load_dotenv()
        import os

        self._path = os.getenv(f"dxhr_{self.version.value}_{self.platform.value}")

        if self._path is None:
            raise FileNotFoundError
        else:
            return self._path

    @staticmethod
    def _match_unpack_from(platform):
        match platform:
            case Bigfile.Platform.XBOX360:
                return "bigfile"
            case Bigfile.Platform.WII_U:
                return "bigfile-wiiu"
            case Bigfile.Platform.PC:
                return "bigfile"
            case Bigfile.Platform.PS3:
                return "cache"
            case _:
                raise BigfileError

    @classmethod
    def from_env(
        cls, version: Optional[Version] = None, platform: Optional[Platform] = None
    ):
        from dotenv import load_dotenv

        load_dotenv()
        obj = cls()

        if version is None or platform is None:
            v, p = cls._parse_env_default()
            obj.version = v
            obj.platform = p
        else:
            if not Bigfile.is_version_valid(version, platform):
                raise BigfileError
            obj.version = version
            obj.platform = platform

        obj.unpack_from = cls._match_unpack_from(obj.platform)
        return obj

    @classmethod
    def from_path(cls, path: str | Path, version: Optional[Version] = None):
        obj = cls()
        obj._path = Path(path).parent
        obj.unpack_from = Path(path).stem
        obj.version = version
        return obj

    @staticmethod
    def _parse_env_default():
        import os

        version = os.getenv("version")
        platform = os.getenv("platform")

        if Bigfile.is_version_valid(
            Bigfile.Version(version), Bigfile.Platform(platform)
        ):
            return Bigfile.Version(version), Bigfile.Platform(platform)
        else:
            raise BigfileError(
                f"Invalid version/platform combination: {version}, {platform}"
            )

    @staticmethod
    def is_version_valid(version: Version, platform: Platform):
        match platform:
            case Bigfile.Platform.PC:
                if version == Bigfile.Version.JAPAN:
                    return False
            case Bigfile.Platform.WII_U:
                if not version == Bigfile.Version.DIRECTORS_CUT:
                    return False
            case _:
                pass

        return True

    def __repr__(self):
        return f"<Bigfile version={self.version} platform={self.platform}>"


if __name__ == "__main__":
    bf = Bigfile.from_env()
    bf.open()
    breakpoint()
