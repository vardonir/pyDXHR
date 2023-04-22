from typing import *
from tqdm import tqdm
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM
from pyDXHR.cdcEngine.Archive import Archive


class MasterunitDRM:
    def __init__(self,
                 masterunit_name: str,
                 archive: Archive,
                 **kwargs
                 ):
        self._unit_list: Dict[str, UnitDRM] = {}
        self._archive: Archive = archive
        self._linked_drm_names: List[str] = []
        self._kwargs = kwargs

        self.Name: str = masterunit_name
        self._read_masterunit()

        for linked in self._linked_drm_names:
            print(f"\n Processing unit {linked}")

            filename = linked + ".drm"
            drm_data = self._archive.get_from_filename(filename)

            unit = UnitDRM()
            unit.deserialize(drm_data, archive=self._archive, kwargs=kwargs)
            self._unit_list[linked] = unit

        breakpoint()

    def _read_masterunit(self):
        name = self.Name if self.Name.endswith("__masterunit.drm") else self.Name + "__masterunit.drm"

        mu_data = self._archive.get_from_filename(name)
        unit = UnitDRM()
        unit.deserialize(mu_data, archive=self._archive, kwargs=self._kwargs)
        self._unit_list[self.Name] = unit
        self._linked_drm_names = unit.linked_drm()

    def _read_drm(self, drm: UnitDRM):
        pass

    def to_gltf(self, save_to):
        from pyDXHR.utils.gltf import merge_multiple
        pass
