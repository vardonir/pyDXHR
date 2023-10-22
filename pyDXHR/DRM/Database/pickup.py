from typing import Optional, Dict, List

from pyDXHR.DRM.utils import get_text_references
from pyDXHR.locals import Locals


class PickupDatabase:
    def __init__(self):
        self._is_open: bool = False
        self._locals_bin: Optional[Locals] = None
        self._drm = None
        self.data = {}

    def set_locals_bin(self, locals_bin: Locals):
        if self._is_open:
            raise RuntimeError("Cannot set locals.bin after opening the database")

        self._locals_bin = locals_bin
        self._locals_bin.open()

    @classmethod
    def from_bigfile(cls, bf, locale: Optional[int] = 0xFFFFFD61):
        """ Open the pickup database from a bigfile """
        from pyDXHR.DRM import DRM

        obj = cls()
        obj._drm = DRM.from_bigfile("pickup_database.drm", bf)

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
            thumbnail_path_variant1 = ref.deref(0x4).access_string()
            thumbnail_path_variant2 = ref.deref(0xC).access_string()

            texture_reference_1 = ref.deref(0x8)
            texture_reference_2 = ref.deref(0x10)
            # ^ these seem to be the same?

            test3c = ref.deref(0x14)
            if test3c:
                cfx_length = test3c.access("L")
                cfx_data = test3c.section.data[0x4:0x4 + cfx_length]
                # if cfx_data[:3] != b"CFX":
                #     breakpoint()
            # else:
            #     breakpoint()

        breakpoint()
