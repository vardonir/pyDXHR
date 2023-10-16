"""
Read bigfile header
"""

from pyDXHR.generated.bigfile_header import BigfileHeader as KaitaiBigfileHeader


class InvalidBigfileDataAlignment(Exception):
    """Raised when the data alignment is not one of the known values"""

    pass


class BigfileHeader(KaitaiBigfileHeader):
    """Bigfile header"""

    def __init__(self, _io, _parent=None, _root=None):
        super().__init__(_io=_io, _parent=_parent, _root=_root)

    @property
    def is_le(self):
        """is bigfile little endian"""
        return self.alignment > 65535

    @property
    def data_alignment(self):
        """bigfile data alignment - flips if necessary + will also check if it's valid"""
        import struct

        match self.alignment:
            case 0x7FF00000:
                return self.alignment

            # ps3 (all versions) + xbox cache = 0x0000F07F
            # xbox base bigfile = 0x00003062
            # xbox demo bigfile = 0x00000065
            # xbox dc disc 1 bigfile = 0x0000D06A
            # xbox dc disc 2 bigfile = 0x0000006B
            # wiiu = 0x0000401
            case 0x0000F07F | 0x00003062 | 0x00000065 | 0x0000D06A | 0x0000401F | 0x0000006B:
                return struct.unpack(">L", struct.pack("<L", self.alignment))[0]

            case _:
                raise InvalidBigfileDataAlignment(f"Found {self.alignment}")

    @property
    def file_headers(self):
        """headers for the files in the bigfile (offset, sizes, locale)"""
        return self.bigfile_data.file_headers

    @property
    def platform_key(self):
        """bigfile platform key, stripped from KSY"""
        return self.bigfile_data.platform.strip("\x00")

    @property
    def file_hashes(self):
        """hashes for the files in the bigfile"""
        return self.bigfile_data.hash_table
