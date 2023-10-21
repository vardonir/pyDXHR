import struct
from typing import Optional, Dict

from pyDXHR.DRM.utils import get_text_references
from pyDXHR.locals import Locals
from pyDXHR.DRM.Section import Section
from pyDXHR.DRM.resolver import Reference


class Computer:
    def __init__(self):
        self.loc_username: int = 0
        self.loc_password: int = 0

        self.username: Optional[str] = None
        self.password: Optional[str] = None

        self.is_modified: bool = False

    @classmethod
    def from_dtp(cls, sec: Section, local_bin: Optional[Locals] = None):
        obj = cls()

        unk1, unk2, obj.loc_username, obj.loc_password = struct.unpack_from("4H", sec.data)

        if local_bin:
            obj.username = local_bin[obj.loc_username]
            obj.password = local_bin[obj.loc_password]

        return obj

    def __repr__(self):
        return f"<Computer: {self.username} / {self.password}>"


class EmailContents:
    def __init__(self):
        self.loc_id_from: int = 0
        self.loc_id_to: int = 0
        self.loc_id_subject: int = 0
        self.loc_id_body: int = 0

        self.email_from: Optional[str] = None
        self.email_to: Optional[str] = None
        self.email_subject: Optional[str] = None
        self.email_body: Optional[str] = None

        self.is_modified: bool = False

    @classmethod
    def from_dtp(cls, sec: Section, local_bin: Optional[Locals] = None):
        obj = cls()

        obj.loc_id_from, obj.loc_id_to, obj.loc_id_subject, obj.loc_id_body = struct.unpack_from("4H", sec.data)

        if local_bin:
            obj.email_from = local_bin[obj.loc_id_from]
            obj.email_to = local_bin[obj.loc_id_to]
            obj.email_subject = local_bin[obj.loc_id_subject]
            obj.email_body = local_bin[obj.loc_id_body]

        return obj

    def __repr__(self):
        return f"<EmailContents: {self.email_subject} from {self.email_from} to {self.email_to}>"

    def modify(self, *,
               from_: Optional[str] = None,
               to: Optional[str] = None,
               subject: Optional[str] = None,
               body: Optional[str] = None):
        if from_:
            self.email_from = from_
            self.is_modified = True
        if to:
            self.email_to = to
            self.is_modified = True
        if subject:
            self.email_subject = subject
            self.is_modified = True
        if body:
            self.email_body = body
            self.is_modified = True


class EmailDatabase:
    def __init__(self):
        self._is_open: bool = False
        self._locals_bin: Optional[Locals] = None
        self._drm = None
        self.data: Dict[int, EmailContents] = {}
        self.computers: Dict[int, Computer] = {}

    @classmethod
    def from_bigfile(cls, bf, locale: Optional[int] = 0xFFFFFD61):
        """ Open the email database from a bigfile """
        from pyDXHR.DRM import DRM

        obj = cls()
        obj._drm = DRM.from_bigfile("email_database.drm", bf)

        if locale is not None:
            obj._locals_bin = Locals.from_bigfile(bf, locale=locale)
            obj._locals_bin.open()

        obj._drm.open()
        return obj

    def set_locals_bin(self, locals_bin: Locals):
        if self._is_open:
            raise RuntimeError("Cannot set locals.bin after opening the database")

        self._locals_bin = locals_bin
        self._locals_bin.open()

    def open(self):
        if self._is_open:
            return

        self._is_open = True
        text_references = get_text_references(self._drm)

        for ref in text_references:
            if ref.section.header.section_id == 32047:
                # email without a sender photo
                # breakpoint()
                pass
            if ref.section.header.section_id == 32048:
                # email with a sender photo
                # breakpoint()
                pass

            mail = EmailContents.from_dtp(ref.section, local_bin=self._locals_bin)
            self.data[ref.section.header.section_id] = mail

            # EXPERIMENTAL - ???
            if ref.deref(0x8).access_string() != "null":
                breakpoint()
            if ref.deref(0x20).access_string() != "null":
                test3 = ref.deref(0x20).access("L")
                test4 = [sec.header.section_id for sec in self._drm.sections].index(test3)
                test5 = self._drm.sections[test4]
                test5a = Reference.from_section_index(self._drm, test4)

                if test5a.deref(0x4) is None:
                    unk1, unk2, loc_user, loc_pw = struct.unpack_from("4H", test5.data)
                    user = self._locals_bin[loc_user]
                    pw = self._locals_bin[loc_pw]
                    # seems to be user/pw combinations but it's incomplete?
                    # print(user, pw)
                else:
                    continue
                    # TODO

            if ref.deref(0x10):
                unk3, unk4, unk5 = struct.unpack_from("LHH", ref.deref(0x10).section.data)
                some_texture = ref.deref(0x10).deref(0x4)
                # print(ref.section.header.section_id, unk4, mail.email_from)
                # breakpoint()

            if ref.deref(0x18):
                # seems to indicate if the email is part of a quest?
                # breakpoint()
                pass

        # EXPERIMENTAL - login/pw combinations, only works with PC DC
        # note: starts at offset 62848
        # there's only 79 computers in the entire game?
        for i in range(55, 134):
            sec = self._drm.sections[i]
            computer = Computer.from_dtp(sec, local_bin=self._locals_bin)
            self.computers[sec.header.section_id] = computer

            # unk1, unk2, loc_user, loc_pw = struct.unpack_from("4H", sec.data)
            # user = self._locals_bin[loc_user]
            # pw = self._locals_bin[loc_pw]

        # breakpoint()

    def __getitem__(self, item):
        return self.data[item]

    def write(self):
        """ Apply modifications to the locals.bin file """
        if not self._is_open:
            raise RuntimeError("Cannot write to a closed database")
        if not self._locals_bin:
            raise FileNotFoundError

        for email in self.data.values():
            if email.is_modified:
                self._locals_bin.modify_at_index(email.loc_id_from, email.email_from)
                self._locals_bin.modify_at_index(email.loc_id_to, email.email_to)
                self._locals_bin.modify_at_index(email.loc_id_subject, email.email_subject)
                self._locals_bin.modify_at_index(email.loc_id_body, email.email_body)

        return self._locals_bin
