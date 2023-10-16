"""
Used for reading/parsing a single entry from a bigfile
"""


class BigfileEntry:
    """
    Single bigfile entry
    """

    __slots__ = (
        "name_hash",
        "filename",
        "locale",
        "offset",
        "uncompressed_size",
        "compressed_size",
        "byte_data",
    )

    def __init__(self):
        self.name_hash: int = 0
        self.filename: str = ""
        self.locale: int = 0
        self.offset: int = 0
        self.uncompressed_size: int = 0
        self.compressed_size: int = 0
        self.byte_data: bytes = b""

    def __repr__(self):
        if len(self.filename):
            return f"<BigfileEntry filename={self.filename}, locale={self.locale}>"

        return f"<BigfileEntry hash={self.name_hash}, locale={self.locale}>"
