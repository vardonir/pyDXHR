from pyDXHR.DRM.utils import get_text_references


class IReaderDatabase:
    def __init__(self):
        self._is_open = False
        self.drm = None

    @classmethod
    def from_bigfile(cls, bf):
        from pyDXHR.DRM import DRM

        obj = cls()
        obj.drm = DRM.from_bigfile("ireader_database.drm", bf)
        obj.drm.open()
        return obj

    def open(self):
        self._is_open = True
        text_references = get_text_references(self.drm)

        breakpoint()
