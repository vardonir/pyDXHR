"""
Work in progress
"""
import struct

locals_bin = r"F:\Game_Rips\deus-ex-human-revolution\raw\gibbed_dc\FFFFFD61\pc-w\local\locals.bin"
locals_fr = r"F:\Game_Rips\deus-ex-human-revolution\raw\gibbed_dc\FFFFFD64\pc-w\local\locals.bin"

# locals_bin = r"F:\DXHRDC_Unpacked\FFFFFD61\pc-w\local\locals.bin"
# locals_fr = r"F:\DXHRDC_Unpacked\FFFFFD64\pc-w\local\locals.bin"

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

# with open(locals_fr, "rb") as f:
#     data_fr = f.read()

strings_en = []
for prev, curr in zip(loc_en.u5, loc_en.u5[1:]):
    # strings_en.append(data_en[prev.str_offset:curr.str_offset].decode("latin1"))
    if curr.str_offset > prev.str_offset:
        strings_en.append(data_en[prev.str_offset:curr.str_offset])
    else:
        breakpoint()

# there's bits in the table that become zero for some reason. doesnt seem to have a pattern. kinda weird

# strings_fr = []
# for prev, curr in zip(loc_fr.u5, loc_fr.u5[1:]):
#     strings_fr.append(data_fr[prev.str_offset:curr.str_offset].decode("latin1"))


# breakpoint()
# a = None
# for idx, i in enumerate(loc.u5):
#     if i.str_offset == 0xe0920:
#         a = idx

# step1 - change the text
# index = 427
# replacement_text = "Testing McTesterson".encode("latin1") + b"\x00"
# note that the replacement text is not the same length as the original text in string_en[index]

index = 2
replacement_text = "Testing McTesterson".encode("latin1") + b"\x00"

# new_str_length = len(replacement_text)
len_difference = len(replacement_text) - len(strings_en[index])

# string_en[0] actually doesnt contain any actual text, but the byte data of the header table, so we can change the value of the offset there
# strings_en[0][0x8:].index(loc_en.u5[index].str_offset)
offsets = [i for i, in struct.iter_unpack("L", strings_en[0][0x8:])]
for i in range(index+1, len(offsets)):
    offsets[i] += len_difference

strings_en[index] = replacement_text

# offsets must be monotonically increasing! <- check me
table = strings_en[0][:0x8]
for off in offsets:
    table += struct.pack("<L", off)

assert len(table) == len(strings_en[0])

# 2 - pack the text back to locals.bin
data = b''
for text in strings_en[1:]:
    # todo: make sure that all the text is byte-terminated
    data += text

rev = table + data
revised_locals = Locals.from_bytes(rev)

strings_new = []
for prev, curr in zip(revised_locals.u5, revised_locals.u5[1:]):
    # strings_new.append(rev[prev.str_offset:curr.str_offset].decode("latin1"))
    strings_new.append(rev[prev.str_offset:curr.str_offset])

# 4 - ???

for idx, (en, revd) in enumerate(zip(strings_en, strings_new)):
    if en != revd:
        breakpoint()

    if len(en) != len(revd):
        breakpoint()

breakpoint()
