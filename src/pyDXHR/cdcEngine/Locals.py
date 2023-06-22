from pyDXHR.cdcEngine.Archive import Archive
from typing import *

# region ------------
# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class KaitaiLocals(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.unk0 = self._io.read_bytes(4)
        self.len_strings = self._io.read_u2le()
        self.unk6 = self._io.read_bytes(2)
        self.str_list = []
        for i in range(self.len_strings):
            self.str_list.append(Locals.String(self._io, self, self._root))

    class String(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset = self._io.read_u4le()

        @property
        def body(self):
            if hasattr(self, '_m_body'):
                return self._m_body

            _pos = self._io.pos()
            self._io.seek(self.offset)
            self._m_body = self._io.read_bytes_term(0, False, True, True)
            self._io.seek(_pos)
            return getattr(self, '_m_body', None)

# endregion -------------------


class Locals(KaitaiLocals):
    def __init__(self, _io, _parent=None, _root=None):
        super().__init__(_io, _parent, _root)
        self.LocalizationLanguage: int = 0xFFFFFD61  # set to English by default
        self.Encoding: str = "latin1"

    def find_string_index(self, string: str | bytes) -> List[int]:
        if isinstance(string, str):
            string = string.encode(self.Encoding)

        return [idx for idx, s in enumerate(self.str_list) if s.body == string]

    def find_string_with_offset(self, offset: int) -> List[int]:
        return [idx for idx, s in enumerate(self.str_list) if s.offset == offset]

    def get_string(self, index: int, decode: bool = False) -> str | bytes:
        """ Mostly used for the in-game databases like email_database.drm, etc """
        if decode:
            return self.str_list[index].body.decode(self.Encoding)
        else:
            return self.str_list[index].body

    @classmethod
    def from_archive(cls, arc: Archive, language: int = 0xFFFFFD61):
        locals_bin = arc.get_from_filename(r"local\locals.bin", spec=language)
        return cls.from_bytes(locals_bin)

    def modify(self, index: int, replacement_text: str | bytes):
        import struct
        head_blob = self.unk0 + struct.pack("<H", self.len_strings) + self.unk6

        final_blob = head_blob + self._rebuild_tables(index, replacement_text)

        new_locals = Locals.from_bytes(final_blob)
        new_locals.LocalizationLanguage = self.LocalizationLanguage
        new_locals.Encoding = self.Encoding
        new_locals.unk0 = self.unk0
        new_locals.len_strings = self.len_strings
        new_locals.unk6 = self.unk6
        return new_locals

    def serialize(self) -> bytes:
        import struct
        head_blob = self.unk0 + struct.pack("<H", self.len_strings) + self.unk6

        # rebuild the offset table
        offsets_blob = b""
        for i, s in enumerate(self.str_list):
            if s.offset == 0:
                offsets_blob += struct.pack("<L", 0)
            else:
                offsets_blob += struct.pack("<L", s.offset)

        # rebuild the string table
        strings_blob = b""
        for i, s in enumerate(self.str_list):
            if i == 0:
                continue
            if len(s.body) == 0:
                strings_blob += b""
                continue

            strings_blob += s.body + b"\x00"

        return head_blob + offsets_blob + strings_blob

    def _rebuild_tables(self, index: int, replacement_text: str | bytes):
        import struct

        original_text = self.get_string(index)

        if isinstance(replacement_text, str):
            replacement_text = replacement_text.encode(self.Encoding)

        len_difference = len(replacement_text) - len(original_text)

        # rebuild the offset table
        offsets_blob = b""
        for i, s in enumerate(self.str_list):
            if s.offset == 0:
                offsets_blob += struct.pack("<L", 0)
            elif i > index:
                offsets_blob += struct.pack("<L", s.offset + len_difference)
            else:
                offsets_blob += struct.pack("<L", s.offset)

        # rebuild the string table
        strings_blob = b""
        for i, s in enumerate(self.str_list):
            if i == 0:
                continue
            if len(s.body) == 0:
                strings_blob += b""
                continue

            if i == index:
                strings_blob += replacement_text + b"\x00"
            else:
                strings_blob += s.body + b"\x00"

        return offsets_blob + strings_blob


if __name__ == "__main__":
    intro_text = r"Welcome to Deus Ex: Human Revolution - Director's Cut. For information and updates, visit www.DeusEx.com or connect to the Internet."

    pc_dc_path = r"F:\Games\Deus Ex HRDC\BIGFILE.000"

    # load the bigfile as an archive instance
    # pc_arc = Archive()
    # pc_arc.deserialize_from_file(pc_dc_path)
    #
    # en_loc_spec = 0xFFFFFD61
    #
    # # get the english locals.bin
    # en_loc_entry = pc_arc.get_from_filename(r"local\locals.bin", spec=en_loc_spec, as_bytes=False)
    # en_loc_data = en_loc_entry.EntryData
    #
    # # clear the entries of the archive
    # pc_arc.Entries = []
    #
    # loc_en = Locals.from_bytes(en_loc_data)
    #
    # index = loc_en.find_string_index(intro_text.encode(using_encoding))
    #
    # if index is None:
    #     breakpoint()
    #
    # replacement_text_str = "hello world -vardonir"
    # replacement_text = replacement_text_str.encode(using_encoding) + b"\x00"
    # original_text = loc_en.str_list[index].body + b"\x00"
    #
    # # new_str_length = len(replacement_text)
    # len_difference = len(replacement_text) - len(original_text)
    #
    # new_blob = loc_en.unk0 + struct.pack("<H", loc_en.len_strings) + loc_en.unk6
    # for i, s in enumerate(loc_en.str_list):
    #     if s.offset == 0:
    #         new_blob += struct.pack("<L", 0)
    #     elif i > index:
    #         new_blob += struct.pack("<L", s.offset + len_difference)
    #     else:
    #         new_blob += struct.pack("<L", s.offset)
    #
    # new_blob_2 = b""
    # for i, s in enumerate(loc_en.str_list):
    #     if i == 0:
    #         continue
    #     if len(s.body) == 0:
    #         new_blob_2 += b""
    #         continue
    #
    #     if i == index:
    #         new_blob_2 += replacement_text
    #     else:
    #         new_blob_2 += s.body + b"\x00"
    #
    #
    # final_blob = new_blob + new_blob_2
    # new_loc = Locals.from_bytes(final_blob)
    #
    # # check for any mismatches besides the lines that were supposed to be changed
    # aa = []
    # for idx, (original, revised) in enumerate(zip(loc_en.str_list, new_loc.str_list)):
    #     if idx == index:
    #         continue
    #
    #     if original.body != revised.body:
    #         aa.append((idx, original.body, revised.body))
    #
    # breakpoint()
    #
    # arc_entry = ArchiveEntry()
    # arc_entry.NameHash = crc32bzip2(r"pc-w\local\locals.bin", dtype=int)
    # arc_entry.Locale = en_loc_spec
    # arc_entry.EntryData = final_blob
    # arc_entry.UncompressedSize = len(final_blob)
    #
    # pc_arc.append(arc_entry)
    #
    # from pathlib import Path
    #
    # new_bigfile = pc_arc.serialize()
    #
    # for idx, byte_data in enumerate(new_bigfile):
    #     output_file = fr"F:\Projects\pyDXHR\output\locals_mod\local.00{idx}"
    #
    #     print(f"Writing to {Path(output_file).name}")
    #     with open(output_file, "wb") as f:
    #         f.write(byte_data)
    #
    # print("Final checks")
    # new_arc = Archive()
    # new_arc.deserialize_from_file(fr"F:\Projects\pyDXHR\output\locals_mod\local.000")
    #
    # breakpoint()
