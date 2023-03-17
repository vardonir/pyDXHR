import struct
from pathlib import Path
import numpy as np
from enum import Enum
from typing import List, Dict, Tuple
from tqdm import tqdm

from cdcEngine.DRM.SectionTypes import SectionType
from utils import Endian
from pyDXHR.cdcEngine.DRM.DRMFile import DRM


class ArchivePlatform(Enum):
    PC_W = "pc-w"
    PC_JAP = "pc-jap"  # this doesn't exist, but it's here for the sake of completeness
    PS3_W = "ps3-w"
    PS3_JAP = "ps3-jap"
    XENON_W = "xenon-w"
    XENON_JAP = "xenon-jap"  # probably not correct lmao
    UNK = ""


class ArchiveEntry:
    def __init__(self):
        self.NameHash: int = 0
        self.Locale: int = 0
        self.Offset: int = 0
        self.CompressedSize: int = 0
        self.UncompressedSize: int = 0

    def __repr__(self):
        return f"{self.NameHash} {hex(self.Locale)} @ {self.Offset} ({self.UncompressedSize} bytes)"


class Archive:
    def __init__(self):
        self.endian: Endian = Endian.Little
        self.data_alignment: int = 0
        self.platform: ArchivePlatform = ArchivePlatform.UNK
        self.number_of_files: int = 0
        self.path: str | Path = ""

        self.Entries: List[ArchiveEntry] = []

    def __repr__(self):
        return f"{self.platform.value} : {self.number_of_files} files"

    def deserialize(self, data: bytes):
        raise NotImplementedError
        # self._deserialize_header(data)
        # self._deserialize_entries(
        #     hash_data=data[0x48:4 * self.number_of_files],
        #     entry_data=data[0x48 + (4 * self.number_of_files):0x48 + (4 * self.number_of_files) + (4 * 4 * self.number_of_files)]
        # )

    def deserialize_from_file(self, file: str | Path):
        # tends to be faster

        self.path = Path(file)
        with open(file, "rb") as f:
            self._deserialize_header(f.read(0x48))

            hash_data = f.read(4 * self.number_of_files)
            entry_data = f.read(4 * 4 * self.number_of_files)

            self._deserialize_entries(hash_data, entry_data)

        # check that the number of files in the folder is as expected
        archive_files = [f for f in Path(file).parent.glob(f"{Path(file).stem}.*") if f.name.split(".")[-1].isnumeric()]
        expected_number_of_archives = np.uint32(0x800 * max([e.Offset for e in self.Entries]) / np.uint64(self.data_alignment) + 1)

        assert len(archive_files) == expected_number_of_archives

    def _deserialize_entries(self, hash_data, entry_data):
        hashes = np.frombuffer(hash_data,
                               dtype=np.dtype(np.uint32).newbyteorder(self.endian.value),
                               count=self.number_of_files)

        entries = np.frombuffer(entry_data,
                                dtype=np.dtype(np.uint32).newbyteorder(self.endian.value),
                                count=4 * self.number_of_files) \
            .reshape((self.number_of_files, 4))

        assert len(np.unique(entries[:, -1], axis=0)) == 1
        assert np.unique(entries[:, -1], axis=0)[0] == 0

        for h, e in zip(hashes, entries):
            archive_entry = ArchiveEntry()
            archive_entry.NameHash = h
            archive_entry.UncompressedSize, archive_entry.Offset, locale, archive_entry.CompressedSize = e
            # archive_entry.Locale = ArchiveLocale(locale)
            archive_entry.Locale = locale

            self.Entries.append(archive_entry)

    def _deserialize_header(self, data: bytes):
        alignment, = struct.unpack_from("<L", data)
        match alignment:
            case 0x7FF00000 | 0x62300000:
                self.endian = Endian.Little
                self.data_alignment = alignment
            case 0x0000F07F | 0x00003062:
                self.endian = Endian.Big
                self.data_alignment, = struct.unpack_from(">L", data)
            case _:
                raise Exception

        game_type = data[4:12].decode("ascii").strip("\x00")
        self.platform = ArchivePlatform(game_type)

        self.number_of_files, = struct.unpack_from(f"{self.endian.value}L", data, offset=0x44)

    def _file_path(self, index):
        return Path("\\".join(self.path.parts[:-1])) / f"{self.path.stem}.{str(index).zfill(3)}"

    def _get_entry_data(self, entry: ArchiveEntry):
        bigfile_index = np.uint32((entry.Offset * 0x800) / np.uint64(self.data_alignment))
        bigfile_offset = np.uint32((entry.Offset * 0x800) % np.uint64(self.data_alignment))

        with open(self._file_path(bigfile_index), "rb") as bigfile:
            bigfile.seek(bigfile_offset)
            data = bigfile.read(entry.UncompressedSize)
        return data

    def get_from_hash(self, file_hash: int | str, spec: int = -1):
        if isinstance(file_hash, str):
            raise NotImplementedError
        else:
            for idx, e in enumerate(self.Entries):
                if e.NameHash == file_hash and e.Locale == np.array(spec).astype(np.uint32).item():
                    return self._get_entry_data(e)

    def get_from_filename(self, file_name: str, spec: int = -1):
        # TODO: use the ArchiveLocale enum instead of the spec integer

        from pyDXHR.utils import crc32bzip2
        if Path(file_name).parts[0] == self.platform.value:
            return self.get_from_hash(crc32bzip2(file_name, dtype=int), spec=spec)
        elif Path(file_name).parts[0] in [i.value for i in ArchivePlatform if i != ArchivePlatform.UNK]:
            rebuilt_filename = "\\".join([self.platform.value] + list(Path(file_name).parts[1:]))
            return self.get_from_hash(crc32bzip2(rebuilt_filename, dtype=int), spec=spec)
        else:
            rebuilt_filename = "\\".join([self.platform.value] + list(Path(file_name).parts))
            return self.get_from_hash(crc32bzip2(rebuilt_filename, dtype=int), spec=spec)

    # region lists
    @property
    def object_list(self):
        return Filenames.object_list(self)

    @property
    def unit_list(self):
        return Filenames.unit_list(self)

    @property
    def section_list(self):
        return Filenames.section_list(self)

    @property
    def animation_list(self):
        return Filenames.animation_list(self)

    @property
    def sound_effects_list(self):
        return Filenames.sound_effects_list(self)

    @property
    def texture_list(self):
        return Filenames.texture_list(self)
    # endregion


class UnpackedArchive(Archive):
    def __init__(self):
        super().__init__()
        self.ArchiveFiles: list = []
        self.SectionHeaders: Dict[Tuple[SectionType, int], List[ArchiveEntry]] = {}

    def unpack(self):
        for entry in tqdm(self.Entries):
            entry_data = self._get_entry_data(entry)
            try:
                drm = DRM()
                drm.deserialize(entry_data, header_only=True)
            except:
                pass
            else:
                self.ArchiveFiles.append(drm)

                for sec_header in drm.Header.SectionHeaders:
                    if sec_header.SectionType == SectionType.Material and sec_header.Specialization >> 30 == 1:
                        continue

                    key = (sec_header.SectionType, sec_header.SecId)
                    if key not in self.SectionHeaders:
                        self.SectionHeaders[key] = []

                    self.SectionHeaders[key].append(entry)
