"""
The locals.bin file contains all the text strings used in the game - from the subtitles,
the menu text, to the emails, and (in the DC version), the director's commentary. This class
reads the locals.bin from a bigfile and allows you to modify the in-game text.

TODO: check encodings for non-English locals.bin files
(I think the French version would be using latin1, the Japanese version uses utf-8, idk about the rest)
"""

from typing import Optional, List
from pyDXHR.Bigfile import Bigfile, BigfileEntry
from pyDXHR.generated.locals import Locals as KaitaiLocals


class Locals:
    def __init__(self):
        self._is_open = False
        self._unk0: bytes = b""
        self._unk6: bytes = b""
        self._entry: Optional[BigfileEntry] = None
        self.byte_data: bytes = b""
        self.encoding: Optional[str] = None
        self.locale: int = 0xFFFFFD61
        self.strings = []
        self._offsets = []

    def __len__(self):
        return len(self.strings)

    @classmethod
    def from_bigfile(
        cls, bf: Bigfile, locale: int = 0xFFFFFD61, encoding: Optional[str] = "utf-8"
    ):
        """
        The default locale here is the English version from the PC Director's Cut
        """
        locals_entry = bf.get_entry_from_filename(r"local\locals.bin", locale=locale)
        locals_bin_bytes = bf.read(r"local\locals.bin", locale=locale)

        obj = cls.from_bytes(locals_bin_bytes)
        obj._entry = locals_entry
        obj.locale = locale
        obj.encoding = encoding
        return obj

    @classmethod
    def from_bytes(cls, data: bytes, encoding: Optional[str] = "utf-8"):
        obj = cls()
        obj.byte_data = data
        obj.encoding = encoding
        return obj

    def open(self):
        self._is_open = True

        kt_locals = KaitaiLocals.from_bytes(self.byte_data)
        self._unk0 = kt_locals.unk0
        self._unk6 = kt_locals.unk6

        for item in kt_locals.str_list:
            if self.encoding is None:
                self.strings.append(item.body)
            else:
                self.strings.append(item.body.decode(self.encoding))
            self._offsets.append(item.offset)

    def offset_dict(self):
        return {o: s for s, o in zip(self.strings, self._offsets)}

    def find_string_index(self, string: str | bytes) -> List[int]:
        """
        Find the index/indices of a string in the locals.bin file

        The problem with using self.strings.index(string) is that you only get the first
        appearance of the string in the list, and there are many duplicates. So if you entered
        self.strings.index("Adam Jensen"), you'll only get 422, whereas the string "Adam Jensen"
        shows up in the game 13 times (in the PC Director's Cut version).
        """

        return [idx for idx, s in enumerate(self.strings) if s == string]

    def find_offset_index(self, offset: int) -> int:
        return self._offsets.index(offset)

    def modify_text(self, original_text: str, replacement_text: str):
        str_index = self.find_string_index(original_text)
        if len(str_index) > 1:
            raise Warning(
                "More than one instance of the string found, this function will replace all instances!"
            )
        for index in str_index:
            self.modify_index(index, replacement_text)

    def modify_index(self, index: int, replacement_text: str | bytes):
        import struct

        head_blob = self._unk0 + struct.pack("<H", len(self)) + self._unk6
        # final_blob = head_blob + self._rebuild_tables(index, replacement_text)
        self.byte_data = head_blob + self._rebuild_tables(index, replacement_text)

    def write(self) -> BigfileEntry:
        test = KaitaiLocals.from_bytes(self.byte_data)
        assert len(self) == len(test.str_list)

        from pyDXHR.Bigfile.filelist import crc32bzip2

        archive_entry = BigfileEntry()
        archive_entry.name_hash = crc32bzip2(r"pc-w\local\locals.bin")
        archive_entry.byte_data = self.byte_data
        archive_entry.locale = self.locale
        archive_entry.offset = self._entry.offset
        archive_entry.compressed_size = self._entry.compressed_size
        archive_entry.uncompressed_size = len(self.byte_data)
        return archive_entry

    def _rebuild_tables(self, index: int, replacement_text: str | bytes):
        import struct

        original_text = self[index]

        if isinstance(replacement_text, str):
            replacement_text = replacement_text.encode(self.encoding)

        len_difference = len(replacement_text) - len(original_text)

        # rebuild the offset table
        offsets_blob = b""
        for i, offset in enumerate(self._offsets):
            if offset == 0:
                offsets_blob += struct.pack("<L", 0)
            elif i > index:
                offsets_blob += struct.pack("<L", offset + len_difference)
            else:
                offsets_blob += struct.pack("<L", offset)

        # rebuild the string table
        strings_blob = b""
        string: str
        for i, string in enumerate(self.strings):
            if i == 0:
                continue
            if len(string) == 0:
                strings_blob += b""
                continue

            if i == index:
                strings_blob += replacement_text + b"\x00"
            else:
                strings_blob += string.encode(self.encoding) + b"\x00"

        return offsets_blob + strings_blob

    def __getitem__(self, item):
        return self.strings[item]
