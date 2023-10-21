"""
Utility for reading and writing the ireader_database.drm file.
"""

import struct
from typing import Optional, Dict

from pyDXHR.DRM.utils import get_text_references
from pyDXHR.locals import Locals
from pyDXHR.DRM.Section import Section


class IReaderContents:
    """
    Class to hold the contents of a single ebook
    """
    def __init__(self):
        self._u3 = -1
        self._u4 = -1
        self._u6 = -1
        self._u7 = -1
        self._u8 = -1

        self.loc_id_author = 0
        self.loc_id_title = 0
        self.loc_id_body = 0

        self.ebook_author: Optional[str] = None
        self.ebook_title: Optional[str] = None
        self.ebook_body: Optional[str] = None

        self.is_modified: bool = False

    @classmethod
    def from_dtp(cls, sec: Section, local_bin: Optional[Locals] = None):
        obj = cls()

        obj.loc_id_author, obj.loc_id_title, obj._u3, \
            obj._u4, obj.loc_id_body, obj._u6, obj._u7, obj._u8 = struct.unpack_from("<8H", sec.data)

        if local_bin:
            if obj.loc_id_author != 0:
                obj.ebook_author = local_bin[obj.loc_id_author]

        obj.ebook_title = local_bin[obj.loc_id_title]
        obj.ebook_body = local_bin[obj.loc_id_body]

        return obj

    def __repr__(self):
        if self.ebook_author is not None:
            return f"<IReaderContents: {self.ebook_title} by {self.ebook_author}>"
        else:
            return f"<IReaderContents: {self.ebook_title}>"

    def modify(self, *,
               title: Optional[str] = None,
               author: Optional[str] = None,
               body: Optional[str] = None,
               exp: Optional[int] = None,
               ):
        self.ebook_body = body if body else self.ebook_body
        self.ebook_title = title if title else self.ebook_title
        self.ebook_author = author if author else self.ebook_author

        # TODO: change EXP value?
        self._u7 = exp if exp else self._u7
        self._u7 = struct.pack("<H", self._u7)

        self.is_modified = True


class IReaderDatabase:
    """ Class for reading the ireader_database.drm """
    def __init__(self):
        self._is_open: bool = False
        self._locals_bin: Optional[Locals] = None
        self._drm = None
        self.data: Dict[int, IReaderContents] = {}

    def set_locals_bin(self, locals_bin: Locals):
        if self._is_open:
            raise RuntimeError("Cannot set locals.bin after opening the database")

        self._locals_bin = locals_bin
        self._locals_bin.open()

    @classmethod
    def from_bigfile(cls, bf, locale: Optional[int] = 0xFFFFFD61):
        """ Open the ireader database from a bigfile """
        from pyDXHR.DRM import DRM

        obj = cls()
        obj._drm = DRM.from_bigfile("ireader_database.drm", bf)

        if locale is not None:
            obj._locals_bin = Locals.from_bigfile(bf, locale=locale)
            obj._locals_bin.open()

        obj._drm.open()
        return obj

    def __getitem__(self, item):
        return self.data[item]

    def open(self):
        self._is_open = True
        text_references = get_text_references(self._drm)

        for ref in text_references:
            if ref.deref(0x14):
                ir = IReaderContents.from_dtp(ref.section, local_bin=self._locals_bin)
                self.data[ref.section.header.section_id] = ir

    def write(self) -> Locals:
        """ Apply modifications to the locals.bin file """
        if not self._is_open:
            raise RuntimeError("Cannot write to a closed database")
        if not self._locals_bin:
            raise FileNotFoundError

        for ebook in self.data.values():
            if ebook.is_modified:
                self._locals_bin.modify_at_index(ebook.loc_id_author, ebook.ebook_author)
                self._locals_bin.modify_at_index(ebook.loc_id_title, ebook.ebook_title)
                self._locals_bin.modify_at_index(ebook.loc_id_body, ebook.ebook_body)

        return self._locals_bin
