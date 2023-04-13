from abc import ABC, abstractmethod
from typing import List, Optional
from pyDXHR.cdcEngine.DRM.Section import Section
from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.utils import Endian


class AbstractSection(ABC):
    def __init__(self, **kwargs):
        self.ID: int = -1
        self.section: Optional[Section] = None
        self._endian: Endian = Endian.Little

        if "section" in kwargs:
            self._deserialize_from_section(kwargs["section"])

        self._archive: Optional[Archive] = kwargs["archive"] if "archive" in kwargs else None
        self._name: Optional[str] = self._get_name_from_archive(self._archive, self.ID)

    @abstractmethod
    def _deserialize_from_section(self, sec):
        self._endian: Endian = sec.Header.Endian
        self.ID = sec.Header.SecId
        self.section = sec

    @staticmethod
    @abstractmethod
    def _get_name_from_archive(archive, sec_id):
        raise NotImplementedError

    @property
    def AttachedArchive(self):
        return self._archive

    @AttachedArchive.setter
    def AttachedArchive(self, archive):
        self._archive = archive
        self._name = self._get_name_from_archive(archive, self.ID)

    @property
    def Name(self) -> str:
        return self._get_name_from_archive(self._archive, self.ID)

    def __eq__(self, other):
        return self.ID == other.ID

    def __hash__(self):
        return self.ID

    @abstractmethod
    def to_gltf(self):
        raise NotImplementedError
