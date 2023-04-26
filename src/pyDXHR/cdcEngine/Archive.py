import dbm
import struct
from pathlib import Path
import numpy as np
from enum import Enum
from typing import List, Dict, Tuple, Optional
from tqdm import tqdm

from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
from pyDXHR.utils import Endian
from pyDXHR.cdcEngine.DRM.DRMFile import DRM


class ArchivePlatform(Enum):
    PC_W = "pc-w"
    PC_JAP = "pc-jap"  # this doesn't exist, but it's here for the sake of completeness
    PS3_W = "ps3-w"
    PS3_JAP = "ps3-jap"
    XENON_W = "xenon-w"
    XENON_JAP = "xenon-jap"  # probably not correct lmao
    WII_W = "wii-w"  # need to check
    UNK = ""

    @staticmethod
    def has_complete_file_lists():
        return (ArchivePlatform.PS3_W.value,
                ArchivePlatform.PS3_JAP.value,
                ArchivePlatform.XENON_W.value)


class ArchiveEntry:
    def __init__(self):
        self.NameHash: int = 0
        self.Locale: int = 0
        self.Offset: int = 0
        self.CompressedSize: int = 0
        self.UncompressedSize: int = 0
        self.EntryData: Optional[bytes] = None

    def __repr__(self):
        return f"{self.NameHash} {hex(self.Locale)} @ {self.Offset} ({self.UncompressedSize} bytes)"


class Archive:
    def __init__(self, **kwargs):
        self.endian: Endian = Endian.Little
        self.data_alignment: int = 0
        self.max_block_size: int = 0
        self.platform: ArchivePlatform = ArchivePlatform.UNK
        self.number_of_files: int = 0
        self.path: str | Path = ""

        self.Entries: List[ArchiveEntry] = []
        # self.EntryDict: Dict[Tuple[int, int], ArchiveEntry] = {}

    def __repr__(self):
        return f"{self.platform.value} : {len(self.Entries)} files"

    def deserialize(self, data: bytes):
        # for, uh, completion?? reading from file tends to be faster
        raise NotImplementedError
        # self._deserialize_header(data)
        # self._deserialize_entries(
        #     hash_data=data[0x48:4 * self.number_of_files],
        #     entry_data=data[0x48 + (4 * self.number_of_files):0x48 + (4 * self.number_of_files) + (4 * 4 * self.number_of_files)]
        # )\

    def deserialize_from_env(self):
        # for one-off tests
        import os
        bigfile = os.getenv('PYDXHR_BIGFILE')
        if bigfile:
            self.deserialize_from_file(bigfile)
        else:
            raise Exception

    def deserialize_from_file(self, file: str | Path):
        # typically used to compare differences between the different game versions

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

            # if (h, locale) in self.EntryDict:
            #     raise Exception
            # self.EntryDict[(h, locale)] = archive_entry

    def _deserialize_header(self, data: bytes):
        alignment, = struct.unpack_from("<L", data)
        match alignment:
            case 0x7FF00000 | 0x62300000:
                self.endian = Endian.Little
                self.data_alignment = alignment
            case 0x0000F07F | 0x00003062:
                self.endian = Endian.Big
                self.data_alignment, = struct.unpack_from(">L", data)

            # alignments im not sure about
            # xbox demo
            case 0x00000065:
                self.endian = Endian.Big
                self.data_alignment, = struct.unpack_from(">L", data)
            # xbox DC
            case 0x0000D06A:
                self.endian = Endian.Big
                self.data_alignment, = struct.unpack_from(">L", data)
            case _:
                raise Exception

        game_type = data[4:12].decode("ascii").strip("\x00")
        self.platform = ArchivePlatform(game_type)
        self.max_block_size = np.uint32(self.data_alignment / 2048)

        self.number_of_files, = struct.unpack_from(f"{self.endian.value}L", data, offset=0x44)

    def _file_path(self, index):
        return Path("\\".join(self.path.parts[:-1])) / f"{self.path.stem}.{str(index).zfill(3)}"

    def get_entry_data(self, entry: ArchiveEntry):
        bigfile_index = np.uint32((entry.Offset * 0x800) / np.uint64(self.data_alignment))
        bigfile_offset = np.uint32((entry.Offset * 0x800) % np.uint64(self.data_alignment))

        with open(self._file_path(bigfile_index), "rb") as bigfile:
            bigfile.seek(bigfile_offset)
            data = bigfile.read(entry.UncompressedSize)

        entry.EntryData = data
        return data

    def get_from_hash(self, file_hash: int | str, spec: int = -1, as_bytes: bool = True):
        if isinstance(file_hash, str):
            raise NotImplementedError
        else:
            # entry = self.EntryDict.get((file_hash, spec))
            #
            # if entry:
            #     if as_bytes:
            #         return self.get_entry_data(entry)
            #     else:
            #         return entry
            # else:
            #     return None

            for idx, e in enumerate(self.Entries):
                if e.NameHash == file_hash and e.Locale == np.array(spec).astype(np.uint32).item():
                    entry_data = self.get_entry_data(e)

                    if as_bytes:
                        return entry_data
                    else:
                        return e

    def get_from_filename(self, file_name: str, spec: int = -1, as_bytes: bool = True, as_raw: bool = False):
        # TODO: use the ArchiveLocale enum instead of the spec integer
        # as_raw = if the input is "xxx/xyz", it will not append the platform prefix. useful for checking the "pc-dev" files

        from pyDXHR.utils import crc32bzip2
        if as_raw:
            return self.get_from_hash(crc32bzip2(file_name, dtype=int), spec=spec, as_bytes=as_bytes)

        if Path(file_name).parts[0] == self.platform.value:
            return self.get_from_hash(crc32bzip2(file_name, dtype=int), spec=spec, as_bytes=as_bytes)
        elif Path(file_name).parts[0] in [i.value for i in ArchivePlatform if i != ArchivePlatform.UNK]:
            rebuilt_filename = "\\".join([self.platform.value] + list(Path(file_name).parts[1:]))
            return self.get_from_hash(crc32bzip2(rebuilt_filename, dtype=int), spec=spec, as_bytes=as_bytes)
        else:
            rebuilt_filename = "\\".join([self.platform.value] + list(Path(file_name).parts))
            return self.get_from_hash(crc32bzip2(rebuilt_filename, dtype=int), spec=spec, as_bytes=as_bytes)

    # region lists
    @property
    def object_list(self):
        obj_list_raw = self.get_from_filename("objectlist.txt")
        if obj_list_raw is None:
            return {}

        return _decode_text(obj_list_raw)

    @property
    def unit_list(self):
        unit_list_raw = self.get_from_filename("unitlist.txt")
        if unit_list_raw is None:
            return []

        unit_list_decoded = [it.decode("ascii") for it in unit_list_raw.split()]
        _ = int(unit_list_decoded.pop(0))
        return unit_list_decoded

    @property
    def section_list(self):
        match self.platform.value:
            case ArchivePlatform.PS3_W.value:
                raw_list = self.get_from_hash(4128657984)  # 0xF6165240
            case ArchivePlatform.PS3_JAP.value:
                raw_list = self.get_from_hash(4162441112)  # F819CF98
            case _:
                return {}

        if raw_list is None:
            return {}

        return _decode_text(raw_list, encoding="latin1")

    @property
    def animation_list(self):
        match self.platform.value:
            case ArchivePlatform.PS3_W.value:
                raw_list = self.get_from_hash(2974621525)  # 0xB14D1F55
            case ArchivePlatform.PS3_JAP.value:
                raise NotImplementedError
            case _:
                return {}

        if raw_list is None:
            return {}

        return _decode_text(raw_list, encoding="latin1")

    @property
    def sound_effects_list(self):
        match self.platform.value:
            case ArchivePlatform.PS3_W.value:
                raw_list = self.get_from_hash(1117682290)  # 0x429E7A72
            case ArchivePlatform.PS3_JAP.value:
                raise NotImplementedError
            case _:
                return {}

        if raw_list is None:
            return {}

        return _decode_text(raw_list, encoding="latin1")

    @property
    def texture_list(self):
        match self.platform.value:
            case ArchivePlatform.PS3_W.value:
                raw_list = self.get_from_hash(2979602415)  # 0xB1991FEF
            case ArchivePlatform.PS3_JAP.value:
                raise NotImplementedError
            case ArchivePlatform.XENON_W.value:
                raise  NotImplementedError
            case _:
                return {}

        if raw_list is None:
            return {}

        return _decode_text(raw_list, encoding="latin1")

    # endregion

    def append(self, entry: ArchiveEntry):
        self.Entries.append(entry)

    def serialize(self):
        out_data = b""
        out_data += struct.pack(f"{self.endian.value}L", self.data_alignment)
        platform_as_bytes = bytes(self.platform.value, 'ascii')

        platform_padding_size = 64 - len(out_data)
        out_data += platform_as_bytes + b"\x00"*platform_padding_size

        out_data += struct.pack(f"{self.endian.value}L", len(self.Entries))

        est_header_size = 4 + 64 + 4 + (4 * (len(self.Entries))) + (16 * len(self.Entries))
        est_header_size += ((0x800 - est_header_size) % 0x800) % 0x800

        self.Entries = sorted(sorted(self.Entries, key=lambda x: x.UncompressedSize), key=lambda y: y.NameHash)

        archive_data = self._repack_archive_entries(est_header_size)

        # pack in the name hashes
        for entry in self.Entries:
            out_data += struct.pack(f"{self.endian.value}L", entry.NameHash)

        # pack in the entry data
        for entry in tqdm(self.Entries, desc="Packing file table"):
            out_data += struct.pack(f"{self.endian.value}L", entry.UncompressedSize)
            out_data += struct.pack(f"{self.endian.value}L", entry.Offset)
            out_data += struct.pack(f"{self.endian.value}L", entry.Locale)
            out_data += struct.pack(f"{self.endian.value}L", entry.CompressedSize)

        # pad header with zeroes
        len_diff = ((0x800 - len(out_data)) % 0x800) % 0x800
        out_data += b"\x00" * len_diff

        # add the first archive data
        out_data += archive_data[0]

        # pad it again with zeroes
        len_diff = ((0x800 - len(out_data)) % 0x800) % 0x800
        out_data += b"\x00" * len_diff

        if len(archive_data) > 1:
            out = [out_data]
            out.extend(archive_data[1:])
            return out
        else:
            return [out_data]

    def _repack_archive_entries(self, header_size: int) -> List[bytes]:
        out_data_list: List[bytes] = [b'']

        max_blocks_per_file = self.data_alignment // 2048

        current_bigfile_index = 0
        global_pos = 0
        pos = header_size // 0x800

        for entry_idx, entry in tqdm(enumerate(self.Entries), desc="Aligning BIGFILEs"):
            if entry.EntryData is None:
                raise Exception
            if entry.UncompressedSize == 0:
                raise Exception
            if entry.CompressedSize:
                raise NotImplementedError

            block_count = (len(entry.EntryData) + 0x800 - 1) // 0x800
            if block_count > max_blocks_per_file:
                block_count = max_blocks_per_file

            if pos + block_count > max_blocks_per_file:
                pos = 0
                global_pos += max_blocks_per_file

                len_diff = ((0x800 - len(out_data_list[current_bigfile_index])) % 0x800) % 0x800
                out_data_list[current_bigfile_index] += b"\x00" * len_diff

                out_data_list.append(b"")
                current_bigfile_index += 1

            # add the entry
            entry.Offset = global_pos + pos
            out_data_list[current_bigfile_index] += entry.EntryData

            # pad this entry with zeros
            len_diff = ((0x800 - len(out_data_list[current_bigfile_index])) % 0x800) % 0x800
            out_data_list[current_bigfile_index] += b"\x00" * len_diff
            pos += block_count

        print(f"Created {current_bigfile_index} BIGFILES")
        return out_data_list


class UnpackedArchive(Archive):
    def deserialize(self, data: bytes):
        super().deserialize(data)

    def __init__(self):
        super().__init__()
        self.ArchiveFiles: list = []
        self.SectionHeaders: Dict[Tuple[SectionType, int], List[ArchiveEntry]] = {}

    def unpack(self, save_db: Optional[Path | str] = None, flag: str = 'c'):
        # https://docs.python.org/3/library/dbm.html#dbm.open
        read_header_only = False if save_db else True
        if save_db:
            raise NotImplementedError
            # db = dbm.open(save_db, flag)

        for entry in tqdm(self.Entries):
            entry_data = self.get_entry_data(entry)
            drm = DRM()

            drm.deserialize(entry_data, header_only=read_header_only)
            if len(drm.Header.SectionHeaders):
                self.ArchiveFiles.append(drm)

                for sec_header in drm.Header.SectionHeaders:
                    if sec_header.SectionType == SectionType.Material and sec_header.Specialization >> 30 == 1:
                        continue

                    key = (sec_header.SectionType, sec_header.SecId)
                    if key not in self.SectionHeaders:
                        self.SectionHeaders[key] = []

                    self.SectionHeaders[key].append(entry)

        # if save_db:
        #     db.close()

    def load_unpacked(self, saved_db: Path | str):
        pass


# region filename stuff
def _decode_text(raw_data: bytes, encoding: str = "ascii"):
    decoded = raw_data.decode(encoding)
    decoded_list = decoded.split("\r")
    return {int(it.split(",")[0].strip()): it.split(",")[1] for it in decoded_list if len(it.split(",")) > 1}
