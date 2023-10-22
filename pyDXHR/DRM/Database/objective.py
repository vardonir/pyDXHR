from typing import Optional, Dict, List

from pyDXHR.DRM.utils import get_text_references
from pyDXHR.locals import Locals


class TaskContents:
    def __init__(self):
        self.task_title: str = ""
        self.task_description: str = ""

    def __repr__(self):
        return self.task_title


class MissionContents:
    def __init__(self):
        self.tasks: List[TaskContents] = []
        self.mission_title: str = ""
        self.mission_description: str = ""
        self.mission_id: int = 0

    def __repr__(self):
        return f"{self.mission_id} | {self.mission_title}"


class ObjectiveDatabase:
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
        """ Open the ireader database from a bigfile """
        from pyDXHR.DRM import DRM

        obj = cls()
        obj._drm = DRM.from_bigfile("objective_database.drm", bf)

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
            test = ref.access("HHIIII")
            test4 = ref.deref(0x24)
            mission_id = test[3]

            test2 = ref.deref(0x8)
            test3 = test2.access("HH")

            task_title = self._locals_bin[test[0]]
            task_desc = self._locals_bin[test[1]]

            mission_title = self._locals_bin[test3[0]]
            mission_desc = self._locals_bin[test3[1]]

            if mission_id not in self.data:
                mission = MissionContents()
                mission.mission_title = mission_title
                mission.mission_description = mission_desc
                mission.mission_id = test[3]
                self.data[mission_id] = mission

            task = TaskContents()
            task.task_title = task_title
            task.task_description = task_desc
            self.data[mission_id].tasks.append(task)

        breakpoint()


