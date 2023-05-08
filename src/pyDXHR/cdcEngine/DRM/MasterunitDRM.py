from typing import *
from pathlib import Path
from tqdm import tqdm, trange
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM
from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.utils import *


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

            unit = UnitDRM(**kwargs)
            unit.deserialize(drm_data, archive=self._archive, **kwargs)
            self._unit_list[linked] = unit

    def _read_masterunit(self):
        print(f"Processing masterunit {self.Name}")
        name = self.Name if self.Name.endswith("__masterunit.drm") else self.Name + "__masterunit.drm"

        mu_data = self._archive.get_from_filename(name)
        unit = UnitDRM(**self._kwargs)
        unit.deserialize(mu_data, archive=self._archive, **self._kwargs)
        self._unit_list[self.Name] = unit
        self._linked_drm_names = unit.linked_drm()

    def to_gltf(self,
                save_to: str,
                action: str = "overwrite",
                blank_materials: bool = False,
                merge: bool = True
                ):
        # from pyDXHR.utils.gltf import merge_multiple

        if Path(save_to).suffix == ".drm":
            save_to = Path(save_to).parent / Path(save_to).stem
        dest = create_directory(save_to=save_to, action=action)

        if merge:
            pass
        else:
            for name, unit in tqdm(self._unit_list.items(), desc="Unit -> GLTF"):
                unit.to_gltf(save_to=dest / name, blank_materials=blank_materials)
