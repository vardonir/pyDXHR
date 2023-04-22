"""
Mostly adapted from https://github.com/rrika/dxhr/blob/main/tools/cdcunit.py

Nodes:
    - transpose???
"""

import os
from pathlib import Path
import warnings
import struct
from tqdm import tqdm, trange
from scipy.spatial.transform import Rotation
import numpy as np
from typing import Dict, List, Any, Optional
from enum import Enum

from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.Reference import Reference
from pyDXHR.utils import create_directory


class ObjectType(Enum):
    IMF = "IMF"
    EXT_IMF = "External IMF"
    OBJ = "OBJ"  # not confusing at all
    Stream = "Stream"
    Collision = "Collision"


class UnitDRM(DRM):
    def __init__(self, **kwargs):
        super().__init__()
        self.ObjectData: Dict[ObjectType, Dict[Any, List[np.ndarray]]] = {}

        self._archive: Optional[Archive] = None
        self._split_objects: bool = False

        self._translation: Optional[List[float]] = kwargs.get("translation")
        self._rotation: Optional[List[float]] = kwargs.get("rotation")
        self._scale: Optional[List[float]] = kwargs.get("scale")
        self._trs_mat: Optional[np.ndarray] = kwargs.get("matrix")

        if "uniform_scale" in kwargs:
            self._scale = 3 * [kwargs["uniform_scale"]]

        if "z_up" in kwargs:
            self._rotation = Rotation.from_euler('x', -90, degrees=True).as_quat().tolist()

        self._rel_count: int = 0
        self._coll_count: int = 0
        self._obj_count: int = 0
        self._obj2_count: int = 0
        self._imf_count: int = 0
        self._streamgroup_count: int = 0
        self._cell_count: int = 0

        self._linked_drm_ref: Reference | None = None
        self._collision_ref: Reference | None = None
        self._obj_ref: Reference | None = None
        self._imf_ref: Reference | None = None
        self._streamgroup_ref: Reference | None = None

        self._cell_ref_list: List[Reference] | None = None
        self._occlusion_ref_list: List[Reference] | None = None

    # region sub0 - linked drm and collision
    def linked_drm(self):
        return [self._linked_drm_ref.get_string(0x100 * i, "utf-8") for i in range(self._rel_count)]

    def _process_collision(self):
        # TODO
        for i in range(self._coll_count):
            cd0s = self._collision_ref.add_offset(i * 0x80)
            trs_mat = self._collision_ref.access_array("f", 16)
            bbs = self._collision_ref.access_array("f", 12, 0x40)

            cd1 = self._collision_ref.deref(0x74)
            vtx = cd1.deref(0x20)
            idx = cd1.deref(0x24)
        return []
    # endregion

    # region sub30 - imf and obj
    def _process_imf(self,
                     skip_ext_imf: bool = False,
                     skip_int_imf: bool = False
                     ):
        ext_imf_dict: Dict[str, List[np.ndarray]] = {}
        imf_dict: Dict[int, List[np.ndarray]] = {}

        for i in trange(self._imf_count, desc="Reading IMF data"):
            trs_mat = self._imf_ref.access_array("f", 16, i * 0x90)
            trs_mat = np.asarray(trs_mat).reshape((4, 4)).T

            dtpid = self._imf_ref.access("I", i * 0x90 + 0x48)
            fname_ref = self._imf_ref.deref(0x4C + i * 0x90)

            if dtpid and not fname_ref:            # IMFs embedded in the file
                dtp_imf_ref = self.lookup_reference(section_type=SectionType.DTPData, section_id=dtpid)
                rm_imf_ref = dtp_imf_ref.deref(0x4)
                rm_sec = rm_imf_ref.section

                if rm_sec.Header.SecId not in imf_dict:
                    # this will probably not trigger, but just in case...
                    imf_dict[rm_sec.Header.SecId] = []
                imf_dict[rm_sec.Header.SecId].append(trs_mat)
            elif not fname_ref:
                pass
            else:           # IMFs elsewhere
                fname = fname_ref.get_string()
                if fname not in ext_imf_dict:
                    ext_imf_dict[fname] = []

                ext_imf_dict[fname].append(trs_mat)

        if not skip_int_imf:
            self.ObjectData[ObjectType.IMF] = imf_dict

        if not skip_ext_imf:
            self.ObjectData[ObjectType.EXT_IMF] = ext_imf_dict

    def _get_obj_indices(self):
        # seems like there's a correlation between that and the list of linked DRMs

        # from collections import Counter
        # c = Counter(self.obj)
        # c["mapboundary"]

        obj_indices = []
        for i in trange(self._obj_count, desc="Reading OBJ data"):
            index,  = struct.unpack_from("<H", self._obj_ref.section.Data,
                                         0x30 + self._obj_ref.offset + i * 0x70)
            pos = struct.unpack_from("<fff", self._obj_ref.section.Data,
                                     0x10 + self._obj_ref.offset + i * 0x70)
            rot = struct.unpack_from("<fff", self._obj_ref.section.Data,
                                     self._obj_ref.offset + i * 0x70)
            scl = struct.unpack_from("<fff", self._obj_ref.section.Data,
                                     0x20 + self._obj_ref.offset + i * 0x70)

            rot_as_matrix = Rotation.from_euler("xyz", rot, degrees=False).as_matrix().T

            trs_mat = np.zeros((4, 4))
            trs_mat[0:3, 0:3] = np.diag(scl)
            trs_mat[-1, :] = np.array(list(pos) + [1])
            trs_mat[0:3, 0:3] = rot_as_matrix

            obj_indices.append((index, trs_mat.T))

        return obj_indices

    def _process_obj2(self):
        # ???
        obj2_count = self._obj_ref.access("I", 0x1C)
        pass
    # endregion

    # region sub50 - occlusion, stream
    def _process_occlusion(self):
        # TODO
        pass
        # for i in range(self._cell_count):
        #     breakpoint()

    def _process_streamgroup(self):
        streamgroup_data: Dict[tuple, List[np.ndarray]] = {}
        for i in trange(self._streamgroup_count, desc="Reading stream objects"):
            streamgroup_ref = self._streamgroup_ref.add_offset(i * 0x14)
            streamgroup_name = streamgroup_ref.deref(0x0)
            streamgroup_path = streamgroup_ref.deref(0xC)
            if streamgroup_path:
                streamgroup_name = streamgroup_name.get_string()
                streamgroup_path = streamgroup_path.get_string()
                key = (streamgroup_name.lower(), streamgroup_path.lower())

                if key not in streamgroup_data:
                    streamgroup_data[key] = []

                # TRS mat for streamobjects is 4x4 unit matrix
                streamgroup_data[key].append(np.eye(4).astype(float))

        self.ObjectData[ObjectType.Stream] = streamgroup_data
    # endregion

    def _get_references(self):
        unit_ref = Reference.from_drm_root(self)

        sub0_ref = unit_ref.deref(0)  # Terrain?
        self._linked_drm_ref = sub0_ref.deref(0x4)
        if self._linked_drm_ref:
            self._rel_count = sub0_ref.access("H", 0x2)

        self._collision_ref = sub0_ref.deref(0x18)
        if self._collision_ref:
            self._coll_count = sub0_ref.access("I", 0x14)

        sub30_ref = unit_ref.deref(0x30)
        if sub30_ref:
            self._obj_ref = sub30_ref.deref(0x18)
            self._obj_count = sub30_ref.access("I", 0x14)

            self._imf_ref = sub30_ref.deref(0xA8)
            self._imf_count = sub30_ref.access("I", 0xA4)

        sub50_ref = unit_ref.deref(0x50)  # CellGroupData
        if sub50_ref:
            sub50_0 = sub50_ref.deref(0)  # CellGroupDataHeader
            self._streamgroup_ref = sub50_ref.deref(0xC)  # CellStreamGroupData*
            sub50_14 = sub50_ref.deref(0x14)  # CellData*[] # RDRs here are just the occlusion
            sub50_18 = sub50_ref.deref(0x18)  # CellStreamData (void terrain)

            if sub50_0 and self._streamgroup_ref:
                self._streamgroup_count = sub50_0.access("I", 0xC)

            if sub50_18:
                sub50_18_4 = sub50_18.deref(4)  # ???
                cell_count = sub50_0.access("L")
                self._cell_count = cell_count

            if sub50_14:
                self._cell_ref_list = []
                self._occlusion_ref_list = []
                for i in range(self._cell_count):
                    cell = sub50_14.deref(4 * i)
                    cellsub0 = cell.deref(0)
                    try:
                        cellsub4 = cell.deref(0x4)
                        cellsub4_0 = cellsub4.deref(0x0)
                    except Exception as e:
                        cellsub4_0 = None

                    cellsub20 = cell.deref(0x20)
                    cellname = cellsub0.deref(0x0).get_string()

                    if cellsub4_0:
                        self._cell_ref_list.append((cellsub4_0, cellname))

                    self._occlusion_ref_list.append(cellsub20)

    def deserialize(self, data: bytes, **kwargs):
        super().deserialize(data=data, header_only=False)
        self._get_references()

        self._split_objects = kwargs.get("split_objects", False)

        if kwargs.get("imf", True):
            self._process_imf(
                skip_ext_imf=kwargs.get("skip_ext_imf", False),
                skip_int_imf=kwargs.get("skip_int_imf", False),
            )

        if "archive" not in kwargs:
            warnings.warn("Cannot parse OBJ without attached archive")
            return

        self._archive: Archive = kwargs["archive"]

        if kwargs.get("collision", True):
            self._process_collision()

        if kwargs.get("obj2", True):
            self._process_obj2()

        if kwargs.get("obj", True):
            object_dict: Dict[str, List[np.ndarray]] = {}

            for obj_index, trs_mat in self._get_obj_indices():
                obj_name = self._archive.object_list[obj_index]
                if obj_name not in object_dict:
                    object_dict[obj_name] = []

                object_dict[obj_name].append(trs_mat)

            self.ObjectData[ObjectType.OBJ] = object_dict

        if kwargs.get('stream', True):
            self._process_streamgroup()

        if kwargs.get("occlusion", True):
            self._process_occlusion()

    @staticmethod
    def _read_section_data(rm_section,
                           folder: str,
                           file_name: str,
                           trs_mat: Optional[np.ndarray] = None,
                           dest: Optional[Path | str] = None,
                           apply_scale: bool = False,
                           blank_materials: bool = False,
                           ):
        from pyDXHR.cdcEngine.Sections import RenderResource
        from pyDXHR.cdcEngine.Sections import RenderMesh
        import kaitaistruct
        import shutil

        try:
            rm = RenderMesh.deserialize(rm_section)
        except kaitaistruct.ValidationNotEqualError as e:
            # some RM sections are apparently badly formed? idk
            # warnings.warn("Encountered RenderMesh error")
            pass
        else:
            if rm:
                gltf_object = rm.to_gltf(as_bytes=False, blank_materials=blank_materials)
                node = gltf_object.nodes[0]

                if trs_mat is not None:
                    node.matrix = trs_mat.T.flatten().tolist()

                if dest:
                    pydxhr_texlib = os.getenv('PYDXHR_TEXLIB')

                    if not pydxhr_texlib:
                        raise Exception
                    else:
                        texture_dest = dest / "textures"
                        texture_dest.mkdir(exist_ok=True, parents=True)

                        for img in gltf_object.images:
                            tex_id = img.extras['cdcTextureID']
                            tex_from_lib = RenderResource.from_library(tex_id=tex_id, tex_lib_dir=pydxhr_texlib, as_path=True)
                            shutil.copy(tex_from_lib, texture_dest)
                            img.uri = "..\\" + str(Path("textures") / Path(tex_from_lib).name)
                            img.name = "T_" + f"{tex_id:x}".rjust(8, '0')

                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", category=UserWarning)
                        (dest / folder).mkdir(parents=True, exist_ok=True)
                        gltf_object.save(dest / folder / file_name)
            else:
                pass

    def to_ue5_csv(self,
                   save_to: Path | str,
                   apply_universal_scale: bool = False,
                   action: str = "overwrite"
                   ):
        # the UE5 importer expects to receive blank materials since those are intended to be fixed later. for now.
        # no transformations are added to the gltf nodes, the CSV file + the importer script is supposed to handle it, in theory
        if Path(save_to).suffix == ".drm":
            save_to = Path(save_to).parent / Path(save_to).stem

        import csv
        dest = create_directory(save_to=save_to, action=action)
        csvfile = open(dest / "locations.csv", 'w', newline='')
        csvwriter = csv.writer(csvfile)

        def write_csv_row(row_name: str, trs: np.ndarray):
            # loc, rot, scl = _decompose_trs_matrix(trs, apply_gltf_scale=apply_universal_scale)
            # row = [row_name]
            # row.extend(loc)
            # row.extend(rot)
            # row.extend(scl)
            csvwriter.writerow([row_name] + trs.flatten().tolist())

        if self._archive:
            # streamobjects
            for (name, path), trs_mat_list in tqdm(self.ObjectData[ObjectType.Stream].items(),
                                                   desc="Processing stream objects"):
                drm_data = self._archive.get_from_filename(fr"streamgroups\{path}.drm")
                drm = DRM()
                drm.deserialize(drm_data)

                for sec in drm.Sections:
                    for idx, trs_mat in enumerate(trs_mat_list):
                        if idx == 0:
                            self._read_section_data(rm_section=sec,
                                                    trs_mat=trs_mat,
                                                    folder="stream",
                                                    file_name=f"{name}_" + f"{sec.Header.SecId:x}".rjust(8, '0') + ".gltf",
                                                    dest=dest,
                                                    apply_scale=apply_universal_scale,
                                                    blank_materials=True
                                                    )
                        write_csv_row(f"{name}_" + f"{sec.Header.SecId:x}".rjust(8, '0'), trs_mat)
                        # csvwriter.writerow([f"{name}_" + f"{sec.Header.SecId:x}".rjust(8, '0')] + trs_mat.T.flatten().tolist())

            # external IMFs
            pbar = tqdm(self.ObjectData[ObjectType.EXT_IMF].items(), desc="Processing external IMFs")
            for imf_path, trs_mat_list in pbar:
                imf_name = Path(imf_path).stem
                pbar.set_description(f"Processing {imf_name}")

                drm_data = self._archive.get_from_filename(imf_path)
                drm = DRM()
                drm.deserialize(drm_data)
                for sec in drm.Sections:

                    for idx, trs_mat in enumerate(trs_mat_list):
                        if idx == 0:
                            self._read_section_data(rm_section=sec,
                                                    folder="imf_ext",
                                                    file_name=f"{imf_name}_" + f"{sec.Header.SecId:x}".rjust(8, '0') + ".gltf",
                                                    dest=dest,
                                                    apply_scale=apply_universal_scale,
                                                    blank_materials=True
                                                    )
                        write_csv_row(f"{imf_name}_" + f"{sec.Header.SecId:x}".rjust(8, '0'), trs_mat)
                        # csvwriter.writerow([f"{imf_name}_" + f"{sec.Header.SecId:x}".rjust(8, '0')] + trs_mat.T.flatten().tolist())

            # objects
            pbar = tqdm(self.ObjectData[ObjectType.OBJ].items(), desc="Processing OBJs")
            for obj_name, trs_mat_list in pbar:
                pbar.set_description(f"Processing {obj_name}")
                drm_data = self._archive.get_from_filename(obj_name + ".drm")
                drm = DRM()
                drm.deserialize(drm_data)

                for sec in drm.Sections:
                    for idx, trs_mat in enumerate(trs_mat_list):
                        if idx == 0:
                            self._read_section_data(rm_section=sec,
                                                    trs_mat=trs_mat,
                                                    folder="obj",
                                                    file_name=f"{obj_name}_" + f"{sec.Header.SecId:x}".rjust(8, '0') + ".gltf",
                                                    dest=dest,
                                                    apply_scale=apply_universal_scale,
                                                    blank_materials=True
                                                    )

                        write_csv_row(f"{obj_name}_" + f"{sec.Header.SecId:x}".rjust(8, '0'), trs_mat)

        # internal IMFs
        for rm_id, trs_mat_list in tqdm(self.ObjectData[ObjectType.IMF].items(), desc="Processing internal IMFs"):
            for idx, trs_mat in enumerate(trs_mat_list):
                rm_sec = self.lookup_section(SectionType.RenderMesh, rm_id)

                if idx == 0:
                    self._read_section_data(rm_section=rm_sec,
                                            folder="imf_int",
                                            file_name="RM_" + f"{rm_id:x}".rjust(8, '0') + ".gltf",
                                            dest=dest,
                                            apply_scale=apply_universal_scale,
                                            blank_materials=True
                                            )
                write_csv_row(f"RenderModel_" + f"{rm_sec.Header.SecId:x}".rjust(8, '0'), trs_mat)

        csvfile.close()

    def to_gltf(self,
                apply_universal_scale: bool = False,
                save_to: Optional[Path | str] = None,
                action: str = "overwrite",
                blank_materials: bool = False
                ):
        from utils.gltf import merge_single

        if Path(save_to).suffix == ".drm":
            save_to = Path(save_to).parent / Path(save_to).stem
        dest = create_directory(save_to=save_to, action=action)

        location_dir: Dict[str, List[List[float]]] = {}

        def write_to_dir(row_name: str, trs: np.ndarray):
            if row_name not in location_dir:
                location_dir[row_name] = []
            location_dir[row_name].append(trs.T.flatten().tolist())

        if self._archive:
            # streamobjects
            if ObjectType.Stream in self.ObjectData:
                for (name, path), trs_mat_list in tqdm(self.ObjectData[ObjectType.Stream].items(),
                                                       desc="Processing stream objects"):
                    drm_data = self._archive.get_from_filename(fr"streamgroups\{path}.drm")
                    drm = DRM()
                    drm.deserialize(drm_data)

                    for sec in drm.Sections:
                        for idx, trs_mat in enumerate(trs_mat_list):
                            if idx == 0:
                                self._read_section_data(rm_section=sec,
                                                        trs_mat=trs_mat,
                                                        folder="stream",
                                                        file_name=f"{name}_" + f"{sec.Header.SecId:x}".rjust(8, '0') + ".gltf",
                                                        dest=dest,
                                                        apply_scale=apply_universal_scale,
                                                        blank_materials=blank_materials
                                                        )
                            write_to_dir(f"{name}_" + f"{sec.Header.SecId:x}".rjust(8, '0'), trs_mat)

            # external IMFs
            if ObjectType.EXT_IMF in self.ObjectData:
                pbar = tqdm(self.ObjectData[ObjectType.EXT_IMF].items(), desc="Processing external IMFs")
                for imf_path, trs_mat_list in pbar:
                    imf_name = Path(imf_path).stem
                    pbar.set_description(f"Processing {imf_name}")

                    # if imf_name == "det_building_scifi_a_lod":
                    #     breakpoint()

                    drm_data = self._archive.get_from_filename(imf_path)
                    drm = DRM()
                    drm.deserialize(drm_data)
                    for sec in drm.Sections:

                        for idx, trs_mat in enumerate(trs_mat_list):
                            if idx == 0:
                                self._read_section_data(rm_section=sec,
                                                        folder="imf_ext",
                                                        file_name=f"{imf_name}_" + f"{sec.Header.SecId:x}".rjust(8, '0') + ".gltf",
                                                        dest=dest,
                                                        apply_scale=apply_universal_scale,
                                                        blank_materials=blank_materials
                                                        )
                            write_to_dir(f"{imf_name}_" + f"{sec.Header.SecId:x}".rjust(8, '0'), trs_mat)

            # objects
            if ObjectType.OBJ in self.ObjectData:
                pbar = tqdm(self.ObjectData[ObjectType.OBJ].items(), desc="Processing OBJs")
                for obj_name, trs_mat_list in pbar:
                    pbar.set_description(f"Processing {obj_name}")
                    drm_data = self._archive.get_from_filename(obj_name + ".drm")
                    drm = DRM()
                    drm.deserialize(drm_data)

                    for sec in drm.Sections:
                        for idx, trs_mat in enumerate(trs_mat_list):
                            if idx == 0:
                                self._read_section_data(rm_section=sec,
                                                        trs_mat=trs_mat,
                                                        folder="obj",
                                                        file_name=f"{obj_name}_" + f"{sec.Header.SecId:x}".rjust(8, '0') + ".gltf",
                                                        dest=dest,
                                                        apply_scale=apply_universal_scale,
                                                        blank_materials=blank_materials
                                                        )
                            write_to_dir(f"{obj_name}_" + f"{sec.Header.SecId:x}".rjust(8, '0'), trs_mat)

        # internal IMFs
        if ObjectType.IMF in self.ObjectData:
            for rm_id, trs_mat_list in tqdm(self.ObjectData[ObjectType.IMF].items(), desc="Processing internal IMFs"):
                for idx, trs_mat in enumerate(trs_mat_list):
                    rm_sec = self.lookup_section(SectionType.RenderMesh, rm_id)

                    if idx == 0:
                        self._read_section_data(rm_section=rm_sec,
                                                folder="imf_int",
                                                file_name="RenderModel_" + f"{rm_id:x}".rjust(8, '0') + ".gltf",
                                                dest=dest,
                                                apply_scale=apply_universal_scale,
                                                blank_materials=blank_materials
                                                )
                    write_to_dir(f"RenderModel_" + f"{rm_id:x}".rjust(8, '0'), trs_mat)

        merge_single(
            output_path=dest,
            location_table=location_dir,
            split_objects_to_separate_node=self._split_objects,
            translation=self._translation,
            scale=self._scale,
            rotation=self._rotation,
            trs_matrix=self._trs_mat,
        )
