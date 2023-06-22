from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.Section import Section
from pyDXHR.cdcEngine.DRM.Reference import Reference
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
from pyDXHR.cdcEngine.Locals import Locals
from pyDXHR.cdcEngine.Archive import ArchiveEntry
from typing import Optional, Dict


class EMail:
    __slots__ = [
        "id_email",
        "loc_id_from",
        "loc_id_to",
        "loc_id_subject",
        "loc_id_body",
        "email_from",
        "email_to",
        "email_subject",
        "email_body",
        "is_modified",
    ]

    def __init__(self):
        self.id_email: int = 0
        self.loc_id_from: int = 0
        self.loc_id_to: int = 0
        self.loc_id_subject: int = 0
        self.loc_id_body: int = 0
        self.email_from: str = ""
        self.email_to: str = ""
        self.email_subject: str = ""
        self.email_body: str = ""
        self.is_modified: bool = False

    def set_email_sender(self, sender: str):
        self.email_from = sender
        self.is_modified = True

    def set_email_recipient(self, recipient: str):
        self.email_to = recipient
        self.is_modified = True

    def set_email_subject(self, subject: str):
        self.email_subject = subject
        self.is_modified = True

    def set_email_body(self, body: str):
        self.email_body = body
        self.is_modified = True

    @classmethod
    def from_dtp(cls, dtp: Section, local_bin: Optional[Locals] = None):
        import struct

        obj = cls()
        obj.id_email = dtp.Header.SecId
        obj.loc_id_from, obj.loc_id_to, obj.loc_id_subject, obj.loc_id_body = struct.unpack_from("HHHH", dtp.Data)

        if local_bin:
            obj.email_from = local_bin.get_string(obj.loc_id_from)
            obj.email_to = local_bin.get_string(obj.loc_id_to)
            obj.email_subject = local_bin.get_string(obj.loc_id_subject)
            obj.email_body = local_bin.get_string(obj.loc_id_body)
        return obj

    def __repr__(self):
        return f"EMail({self.id_email}) : {self.email_from} -> {self.email_to} : {self.email_subject} : {self.email_body}"


class EmailDatabase(DRM):
    def __init__(self, **kwargs):
        super().__init__()
        self.Emails: Dict[int, EMail] = {}

    def deserialize(self, data: bytes, **kwargs):
        import numpy as np

        des = super().deserialize(data=data, header_only=False)
        if not des:
            breakpoint()

        archive = kwargs.get("arc", None)

        if archive:
            locals_bin = Locals.from_archive(archive)
        else:
            locals_bin = None

        root_ref = Reference.from_drm_root(self)
        header = np.frombuffer(root_ref.section.Data, dtype=np.dtype(np.uint32).newbyteorder(self.Header.Endian.value))
        len_emails = header[0]
        email_text_ids = header[1:]
        assert email_text_ids.size == len_emails

        email_text_refs = [
            self.lookup_reference(SectionType.DTPData, s_id)
            for s_id in email_text_ids
        ]

        # DTPData in start with 8 bytes - 4 uint32s for username and password pairs, refer to locals bin for values
        #
        # looks like something that can be obtained from locals.bin, but idk what it is
        # Reference.from_drm_section(self, self.Sections[191]).deref(0x4).get_string()
        #
        # # ???
        # Reference.from_drm_section(self, self.Sections[891]).deref(0x20)

        for ir, ref in enumerate(email_text_refs):
            ss1 = ref.deref(8).get_string()
            if ss1 != "null":
                breakpoint()

            self.Emails[ref.section.Header.SecId] = EMail.from_dtp(ref.section, locals_bin)

    def modify_locals_bin(self, locals_bin: Locals):
        from copy import deepcopy

        # find any modified emails
        modified_emails = [email for email in self.Emails.values() if email.is_modified]

        modified_locals = None
        for email in modified_emails:
            if modified_locals:
                source_locals = deepcopy(modified_locals)
                modified_locals = None
            else:
                source_locals = deepcopy(locals_bin)

            modified_locals = source_locals.modify(email.loc_id_from, email.email_from)\
                .modify(email.loc_id_to, email.email_to)\
                .modify(email.loc_id_subject, email.email_subject)\
                .modify(email.loc_id_body, email.email_body)

        return modified_locals


if __name__ == "__main__":
    from pyDXHR.cdcEngine.Archive import Archive
    arc = Archive()
    # arc.deserialize_from_env()
    # arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHR 1.0.499.0 beta\BIGFILE.000")
    # arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHRPS3\CACHE.000")
    arc.deserialize_from_file(r"F:\Games\Deus Ex HRDC\BIGFILE.000")

    db = arc.get_from_filename("email_database.drm")
    drm = EmailDatabase()
    drm.deserialize(db, arc=arc, localization=0xFFFFFD61)

    # sample code for replacing an email
    email_id_to_replace = 63313  # the "skull gun" email in sarif's computer
    email_to_replace = drm.Emails[email_id_to_replace]

    email_to_replace.set_email_sender("vardonir@proton.me")
    # email_to_replace.set_email_recipient("")
    email_to_replace.set_email_subject("testing 123")
    email_to_replace.set_email_body("whee")

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
        output_file = fr"F:\Projects\pyDXHR\output\locals_mod\email_mod.00{idx}"

        print(f"Writing to {Path(output_file).name}")
        with open(output_file, "wb") as f:
            f.write(byte_data)

    print("Final checks")
    new_arc = Archive()
    new_arc.deserialize_from_file(fr"F:\Projects\pyDXHR\output\locals_mod\email_mod.000")

    breakpoint()
