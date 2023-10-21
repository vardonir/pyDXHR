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


class LocalsItem:
    def __init__(self):
        self.byte_string: bytes = b""
        self.original_length = 0
        self.string: Optional[str] = None
        self.offset: int = 0
        self.is_modified: bool = False
        self.encoding: Optional[str] = None

    @classmethod
    def from_kaitai_str(cls, kt_string_object, encoding: Optional[str] = "utf-8"):
        obj = cls()

        obj.byte_string = kt_string_object.body
        obj.original_length = len(kt_string_object.body)
        if encoding:
            obj.encoding = encoding
            obj.string = kt_string_object.body.decode(encoding)

        obj.offset = kt_string_object.offset
        return obj

    def __repr__(self):
        return f"<LocalsItem: {self.offset} | {self.string}>"


class Locals:
    def __init__(self):
        self._is_open = False
        self._unk0: bytes = b""
        self._unk6: bytes = b""
        self._entry: Optional[BigfileEntry] = None
        self.byte_data: bytes = b""
        self.encoding: Optional[str] = None
        self.locale: int = 0xFFFFFD61

        self.items: List[LocalsItem] = []

    def __len__(self):
        return len(self.items)

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
        if self._is_open:
            return

        self._is_open = True

        kt_locals = KaitaiLocals.from_bytes(self.byte_data)
        self._unk0 = kt_locals.unk0
        self._unk6 = kt_locals.unk6

        self.items = [LocalsItem.from_kaitai_str(item, self.encoding) for item in kt_locals.str_list]

    @property
    def offset_dict(self):
        if self.encoding:
            return {item.offset: item.string for item in self.items}
        else:
            return {item.offset: item.byte_string for item in self.items}

    def modify_text(self, original: str | bytes, replacement: str | bytes):
        str_index = self._find_string_at_index(original)
        if len(str_index) > 1:
            raise Warning(
                "More than one instance of the string found, this function will replace all instances!"
            )
        for index in str_index:
            self.modify_at_index(index, replacement)

    def modify_at_index(self, index: int, replacement: str | bytes):
        self.items[index].is_modified = True

        if self.encoding:
            self.items[index].string = replacement
        else:
            self.items[index].byte_string = replacement

    def _find_offset_at_index(self, index: int) -> int:
        return self.items[index].offset

    def _find_string_at_index(self, string: str | bytes) -> List[int]:
        """
        Find the index/indices of a string in the locals.bin file

        The problem with using self.strings.index(string) is that you only get the first
        appearance of the string in the list, and there are many duplicates. So if you entered
        self.strings.index("Adam Jensen"), you'll only get 422, whereas the string "Adam Jensen"
        shows up in the game 13 times (in the PC Director's Cut version).
        """

        if self.encoding:
            return [idx for idx, s in enumerate(self.items) if s.string == string]
        else:
            return [idx for idx, s in enumerate(self.items) if s.byte_string == string]

    def _rebuild_tables(self):
        """
        Rebuild the offset table and the text body
        Note: this works even for modifying more than one text item in the table
        """
        import struct

        # build header
        head_blob = self._unk0 + struct.pack("<H", len(self)) + self._unk6

        # calculate where the starting offset of the text blob should be - this is the
        # length of the offset table + length of the header
        text_blob_start = len(self) * 4 + len(head_blob)

        # build text body
        text_blob = b""
        offset_cursor = text_blob_start
        for i in self.items:
            if len(i.string) == 0:
                text_blob += b""
                continue

            if self.encoding:
                data = i.string.encode(self.encoding) + b"\x00"
            else:
                data = i.byte_string + b"\x00"

            i.offset = offset_cursor
            offset_cursor += len(data)
            text_blob += data

        # build offset table
        offset_blob = b""
        for i in self.items:
            offset_blob += struct.pack("<L", i.offset)

        return head_blob + offset_blob + text_blob

    def write(self) -> BigfileEntry:
        blob = self._rebuild_tables()
        test = KaitaiLocals.from_bytes(blob)
        assert len(self) == len(test.str_list)

        # make sure the tests pass before writing
        self.byte_data = blob

        from pyDXHR.Bigfile.filelist import crc32bzip2

        archive_entry = BigfileEntry()
        archive_entry.name_hash = crc32bzip2(r"pc-w\local\locals.bin")
        archive_entry.byte_data = self.byte_data
        archive_entry.locale = self.locale
        archive_entry.offset = self._entry.offset
        archive_entry.compressed_size = self._entry.compressed_size
        archive_entry.uncompressed_size = len(self.byte_data)
        return archive_entry

    def __getitem__(self, index):
        if self.encoding:
            return self.items[index].string
        else:
            return self.items[index].byte_string

    def append(self, text: str):
        raise NotImplementedError
