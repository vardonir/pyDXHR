from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.Section import Section
from pyDXHR.cdcEngine.DRM.Reference import Reference
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
from pyDXHR.cdcEngine.Locals import Locals
from pyDXHR.cdcEngine.Archive import ArchiveEntry
from typing import Optional, Dict


class EBook:
    __slots__ = [
        "id_ebook",
        "loc_id_author",
        "loc_id_title",
        "loc_id_body",

        "ebook_author",
        "ebook_title",
        "ebook_body",

        "is_modified",

        "_u3",  # not sure what this is, but it's sometimes nonzero
        "_u4",  # zeroes
        "_u6",  # zeroes
        "_u7",  # seems to be the ebook achievement flag
        "_u8",  # zeroes
    ]

    def __init__(self):
        self.id_ebook: int = 0
        self.loc_id_author: int = 0
        self.loc_id_title: int = 0
        self.loc_id_body: int = 0

        self.ebook_author: str = ""
        self.ebook_title: str = ""
        self.ebook_body: str = ""

        self.is_modified: bool = False

    def set_ebook_author(self, author: str):
        if len(self.ebook_author):
            self.ebook_author = author
            self.is_modified = True
        else:
            print("Not supported")

    def set_ebook_title(self, title: str):
        self.ebook_title = title
        self.is_modified = True

    def set_ebook_body(self, body: str):
        self.ebook_body = body
        self.is_modified = True

    @classmethod
    def from_dtp(cls, dtp: Section, local_bin: Optional[Locals] = None):
        import struct

        obj = cls()
        obj.id_ebook = dtp.Header.SecId

        obj.loc_id_author, obj.loc_id_title, obj._u3, \
            obj._u4, obj.loc_id_body, obj._u6, obj._u7, obj._u8 = struct.unpack_from("8H", dtp.Data)

        if local_bin:
            if obj.loc_id_author != 0:
                obj.ebook_author = local_bin.get_string(obj.loc_id_author)

        obj.ebook_title = local_bin.get_string(obj.loc_id_title)
        obj.ebook_body = local_bin.get_string(obj.loc_id_body)

        return obj

    def __repr__(self):
        return f"EBook: {self.ebook_title} by {self.ebook_author} | {self.ebook_body[:50]}..."


class IReaderDatabase(DRM):
    def __init__(self, **kwargs):
        super().__init__()
        self.Ebooks: Dict[int, EBook] = {}

    def deserialize(self, data: bytes, **kwargs):
        import numpy as np

        des = super().deserialize(data=data, header_only=False)
        if not des:
            breakpoint()

        archive = kwargs.get("arc", None)

        if archive:
            locals_bin = Locals.from_archive(archive)
            locals_bin.Encoding = "utf8"
        else:
            locals_bin = None

        root_ref = Reference.from_drm_root(self)
        header = np.frombuffer(root_ref.section.Data, dtype=np.dtype(np.uint32).newbyteorder(self.Header.Endian.value))
        len_texts = header[0]
        text_ids = header[1:]
        assert len_texts == text_ids.size

        text_refs = [
            self.lookup_reference(SectionType.DTPData, s_id)
            for s_id in text_ids
        ]

        for ir, ref in enumerate(text_refs):
            self.Ebooks[ref.section.Header.SecId] = EBook.from_dtp(ref.section, locals_bin)

    def modify_locals_bin(self, locals_bin: Locals):
        from copy import deepcopy

        # find any modified ebooks
        modified = [e for e in self.Ebooks.values() if e.is_modified]

        modified_locals = None
        for e in modified:
            if modified_locals:
                source_locals = deepcopy(modified_locals)
                modified_locals = None
            else:
                source_locals = deepcopy(locals_bin)

            modified_locals = source_locals.modify(e.loc_id_body, e.ebook_body)\
                .modify(e.loc_id_author, e.ebook_author)\
                .modify(e.loc_id_title, e.ebook_title)

        return modified_locals


if __name__ == "__main__":
    # use utf8 decode
    from pyDXHR.cdcEngine.Archive import Archive
    arc = Archive()
    # arc.deserialize_from_env()
    # arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHR 1.0.499.0 beta\BIGFILE.000")
    # arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHRPS3\CACHE.000")
    arc.deserialize_from_file(r"F:\Games\Deus Ex HRDC\BIGFILE.000")

    db = arc.get_from_filename("ireader_database.drm")
    drm = IReaderDatabase()
    drm.deserialize(db, arc=arc, localization=0xFFFFFD61)

    # sample code for replacing an ebook
    ebook_id_sample = 32051  # the patient X ebook in megan's office
    ebook = drm.Ebooks[ebook_id_sample]

    ebook.set_ebook_title("Lipsum")
    ebook.set_ebook_author("Test")
    ebook.set_ebook_body("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec auctor, nisl vitae luctus ")

    loc_bin = Locals.from_archive(arc)
    modified_loc_bin = drm.modify_locals_bin(loc_bin)
    new_locals_bin_blob = modified_loc_bin.serialize()

    test_loc_bin = Locals.from_bytes(new_locals_bin_blob)

    breakpoint()

    arc.Entries = []

    from pyDXHR.utils import crc32bzip2

    arc_entry = ArchiveEntry()
    arc_entry.NameHash = crc32bzip2(r"pc-w\local\locals.bin", dtype=int)
    arc_entry.Locale = 0xFFFFFD61
    arc_entry.EntryData = new_locals_bin_blob
    arc_entry.UncompressedSize = len(new_locals_bin_blob)

    arc.append(arc_entry)

    from pathlib import Path
    new_bigfile = arc.serialize()

    for idx, byte_data in enumerate(new_bigfile):
        output_file = fr"F:\Projects\pyDXHR\output\locals_mod\ireader_mod.00{idx}"

        print(f"Writing to {Path(output_file).name}")
        with open(output_file, "wb") as f:
            f.write(byte_data)

    print("Final checks")
    new_arc = Archive()
    new_arc.deserialize_from_file(fr"F:\Projects\pyDXHR\output\locals_mod\ireader_mod.000")

    breakpoint()
