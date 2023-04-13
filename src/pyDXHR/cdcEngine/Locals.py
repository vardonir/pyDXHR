"""
Work in progress
"""

locals_bin = r"C:\Users\vardo\DXHR_Research\DXHRDC_Unpacked\FFFFFD61\pc-w\local\locals.bin"
locals_fr = r"C:\Users\vardo\DXHR_Research\DXHRDC_Unpacked\FFFFFD64\pc-w\local\locals.bin"

# region ------------
# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Locals(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.u1 = self._io.read_u4le()
        self.u2a = self._io.read_u2le()
        self.u2b = self._io.read_u2le()
        self.u5 = []
        for i in range(self.u2a):
            self.u5.append(Locals.Unk(self._io, self, self._root))


    class Unk(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.str_offset = self._io.read_u4le()
# endregion -------------------

loc_en = Locals.from_file(locals_bin)
loc_fr = Locals.from_file(locals_fr)

with open(locals_bin, "rb") as f:
    data_en = f.read()

with open(locals_fr, "rb") as f:
    data_fr = f.read()

strings_en = []
for prev, curr in zip(loc_en.u5, loc_en.u5[1:]):
    strings_en.append(data_en[prev.str_offset:curr.str_offset].decode("latin1"))

strings_fr = []
for prev, curr in zip(loc_fr.u5, loc_fr.u5[1:]):
    strings_fr.append(data_fr[prev.str_offset:curr.str_offset])


# breakpoint()
# a = None
# for idx, i in enumerate(loc.u5):
#     if i.str_offset == 0xe0920:
#         a = idx