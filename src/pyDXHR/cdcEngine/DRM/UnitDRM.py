"""
Mostly adapted from https://github.com/rrika/dxhr/blob/main/tools/cdcunit.py

Notes:
    - why transpose???
    - no, i mean why am i transposing a lot?
"""

import os
from pathlib import Path
import warnings
import struct
from tqdm import tqdm, trange
from scipy.spatial.transform import Rotation
import numpy as np
from typing import *
from enum import Enum

from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
from pyDXHR.cdcEngine.DRM.DRMFile import DRM, Section
from pyDXHR.cdcEngine.DRM.Reference import Reference
from pyDXHR.cdcEngine.Sections.CollisionMesh import CollisionMesh
from pyDXHR.utils import create_directory


class ObjectType(Enum):
    IMF = "IMF"
    EXT_IMF = "External IMF"
    OBJ = "OBJ"  # not confusing at all
    Stream = "Stream"
    Collision = "Collision"
    Cell = "Cell"
    Occlusion = "Occlusion"


class UnitDRM(DRM):
    _identity_trs = np.eye(4).astype(float)

    def __init__(self, **kwargs):
        super().__init__()
        self.ObjectData: Dict[ObjectType, Dict[Any, List[np.ndarray]]] = {}
        self.CellSectionData: List[Section] = []
        self.CollisionMesh: List[CollisionMesh] = []

        self._archive: Optional[Archive] = None
        self._split_objects: bool = False

        self._translation: Optional[List[float]] = kwargs.get("translation")
        self._rotation: Optional[List[float]] = kwargs.get("rotation")
        self._scale: Optional[List[float]] = kwargs.get("scale")
        self._trs_mat: Optional[np.ndarray] = kwargs.get("matrix")

        self._verbose: bool = kwargs.get("verbose", True)

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

        self._linked_drm_ref: Optional[Reference] = None
        self._collision_ref: Optional[Reference] = None
        self._obj_ref: Optional[Reference] = None
        self._imf_ref: Optional[Reference] = None
        self._streamgroup_ref: Optional[Reference] = None

        self._cell_ref_list: Optional[List[Reference]] = None
        self._occlusion_ref_list: Optional[List[Reference]] = None

    # region sub0 - linked drm and collision
    def linked_drm(self) -> List[str]:
        """ Get the names of the DRMs linked to this unit - used specifically for Masterunit DRMs """
        return [self._linked_drm_ref.get_string(0x100 * i, "utf-8") for i in range(self._rel_count)]

    def _process_collision(self) -> None:
        """ Read collision references and generate collision meshes """
        # although, I think it's the same mesh every time...
        self.CollisionMesh = [CollisionMesh(self._collision_ref, offset=i * 0x80) for i in range(self._coll_count)]
    # endregion

    # region sub30 - imf and obj
    def _process_imf(self,
                     skip_ext_imf: bool = False,
                     skip_int_imf: bool = False
                     ) -> None:
        """
        Process IMF references. Will process both internal and external IMFs regardless of input kwargs.
        External IMFs only get the file names + TRS matrix, whereas internal IMFs get the section ID + TRS matrix.
        Processing external IMFs require an attached archive.
        """
        if not self._imf_ref:
            return
            
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
            if self._archive is None:
                warnings.warn("Cannot parse external IMF without attached archive")
            else:
                self.ObjectData[ObjectType.EXT_IMF] = ext_imf_dict

    def _get_obj_indices(self) -> List[Tuple[int, np.ndarray]]:
        """
        Get the indices of the objects in the unit + the associated TRS matrix.
        The actual object names will be taken from the objlist.txt in the attached arcive.
        TODO: some objects seem to be missing, e.g., the cars in det_city_sarif
        """
        if not self._obj_ref:
            return []

        obj_indices = []
        for i in trange(self._obj_count, desc="Reading OBJ data"):
            rot = struct.unpack_from("<fff", self._obj_ref.section.Data,
                                     self._obj_ref.offset + i * 0x70)
            pos = struct.unpack_from("<fff", self._obj_ref.section.Data,
                                     0x10 + self._obj_ref.offset + i * 0x70)
            scl = struct.unpack_from("<fff", self._obj_ref.section.Data,
                                     0x20 + self._obj_ref.offset + i * 0x70)

            index,  = struct.unpack_from("<H", self._obj_ref.section.Data,
                                         0x30 + self._obj_ref.offset + i * 0x70)

            # see: https://en.wikipedia.org/wiki/Euler_angles#Conventions_by_intrinsic_rotations
            # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.from_euler.html
            rot_as_matrix = Rotation.from_euler("XYZ", rot, degrees=False).as_matrix().T

            trs_mat = np.zeros((4, 4))
            trs_mat[0:3, 0:3] = np.diag(scl)
            trs_mat[0:3, 0:3] = rot_as_matrix
            trs_mat[-1, :] = np.array(list(pos) + [1])

            obj_indices.append((index, trs_mat.T))

        return obj_indices
    # endregion

    # region sub50 - occlusion, cell, stream
    def _process_cell(self) -> None:
        """ Process "cells" - RenderTerrain sections embedded in the DRM """
        if self._cell_ref_list:
            self.ObjectData[ObjectType.Cell] = {
                (cell_name, cell.section.Header.SecId): [self._identity_trs]
                for cell, cell_name in self._cell_ref_list
            }

        self.CellSectionData = [cell.section for cell, _ in self._cell_ref_list]

    def _process_occlusion(self) -> None:
        """ Process occlusion boxes. """
        if self._occlusion_ref_list:
            self.ObjectData[ObjectType.Occlusion] = {
                sec.section.Header.SecId: [self._identity_trs]
                for sec in self._occlusion_ref_list
            }

    def _process_streamgroup(self) -> None:
        """ Get streamgroup names - RenderTerrain sections defined outside the DRM. Requires an attached archive. """
        streamgroup_data: Dict[tuple, List[np.ndarray]] = {}
        for i in trange(self._streamgroup_count, desc="Reading stream objects"):
            streamgroup_ref = self._streamgroup_ref.add_offset(i * 0x14)
            streamgroup_name = streamgroup_ref.deref(0x0)
            # num_cells = streamgroup_ref.access("L", 0x4)  # ???
            # cells = streamgroup_ref.deref(0x8)  # ???
            streamgroup_path = streamgroup_ref.deref(0xC)
            if streamgroup_path:
                streamgroup_name = streamgroup_name.get_string()
                streamgroup_path = streamgroup_path.get_string()
                key = (streamgroup_name.lower(), streamgroup_path.lower())

                if key not in streamgroup_data:
                    streamgroup_data[key] = []

                # TRS mat for streamobjects is 4x4 unit matrix...?
                streamgroup_data[key].append(self._identity_trs)

        self.ObjectData[ObjectType.Stream] = streamgroup_data
    # endregion

    def _get_references(self) -> None:

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
            # Refer to: https://github.com/rrika/cdcEngineDXHR/blob/main/cdcScene/cdcSceneCookdata.h
            # struct CellGroupData { // 61
            # 	CellGroupDataHeader *header; // 0
            # 	uint32_t admd_maybe; // 4
            # 	SceneCellBSPNode *bspNodes; // 8
            # 	CellStreamGroupData *streamgroups; // C
            # 	const char **symbols; // 10
            # 	CellData **cells; // 14
            # 	CellStreamData *void_terrain_maybe; // 18
            # 	CellStreamData *exterior_terrain_maybe; // 1C
            # };

            sub50_0 = sub50_ref.deref(0)  # CellGroupDataHeader
            # cell_group_data_header = sub50_0.access_array("L", 7)
            # bsp_nodes = sub50_ref.deref(0x8)
            # test_xyzdist = bsp_nodes.access_array("f", 4)

            self._streamgroup_ref = sub50_ref.deref(0xC)  # CellStreamGroupData*

            sub50_14 = sub50_ref.deref(0x14)  # CellData*[]
            sub50_18 = sub50_ref.deref(0x18)  # CellStreamData (void terrain)
            sub50_1c = sub50_ref.deref(0x1c)  # CellStreamData (exterior terrain)

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
                    cell_sub0 = cell.deref(0)
                    try:
                        cell_sub4 = cell.deref(0x4)
                        cell_sub4_0 = cell_sub4.deref(0x0)
                    except AttributeError:
                        cell_sub4_0 = None

                    cell_sub20 = cell.deref(0x20)
                    cell_name = cell_sub0.deref(0x0).get_string()

                    if cell_sub4_0:
                        self._cell_ref_list.append((cell_sub4_0, cell_name))

                    self._occlusion_ref_list.append(cell_sub20)

    def deserialize(self, data: bytes, **kwargs):
        super().deserialize(data=data, header_only=False)
        self._get_references()
        self._archive: Archive = kwargs.get("archive")
        self._split_objects = kwargs.get("split_objects", False)

        if kwargs.get("imf", True):
            self._process_imf(
                skip_ext_imf=kwargs.get("skip_ext_imf", False),
                skip_int_imf=kwargs.get("skip_int_imf", False),
            )

        if kwargs.get("collision", True):
            self._process_collision()

        if kwargs.get("occlusion", True):
            self._process_occlusion()

        if kwargs.get("cell", True):
            self._process_cell()

        if kwargs.get("obj", True):
            object_dict: Dict[str, List[np.ndarray]] = {}

            if self._archive is None:
                warnings.warn("Cannot parse OBJ without attached archive")
            else:
                for obj_index, trs_mat in self._get_obj_indices():
                    obj_name = self._archive.object_list[obj_index]
                    if obj_name not in object_dict:
                        object_dict[obj_name] = []

                    object_dict[obj_name].append(trs_mat)

                self.ObjectData[ObjectType.OBJ] = object_dict

        if kwargs.get('stream', True):
            if self._archive is None:
                warnings.warn("Cannot parse streamobjects without attached archive")
            else:
                self._process_streamgroup()

    @staticmethod
    def _read_section_data(rm_section,
                           folder: str,
                           file_name: str,
                           trs_mat: Optional[np.ndarray] = None,
                           dest: Optional[Path | str] = None,
                           blank_materials: bool = False,
                           skip_materials: bool = False,
                           ):
        from pyDXHR.cdcEngine.Sections import RenderResource
        from pyDXHR.cdcEngine.Sections import RenderMesh
        import kaitaistruct
        import shutil

        try:
            rm = RenderMesh.deserialize(rm_section)
        except kaitaistruct.ValidationNotEqualError as e:
            # some RM sections are apparently badly formed? they're rare, but they exist
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

    def to_gltf(self,
                apply_universal_scale: bool = False,
                save_to: Optional[Path | str] = None,
                **kwargs
                ):
        # TODO would be nice to separate the unit DRM into smaller sections. Importing to UE5 takes forever...
        from utils.gltf import merge_single

        blank_materials = kwargs.get("blank_materials", False)
        action = kwargs.get("action", "overwrite")
        skip_materials = kwargs.get("skip_materials", False)
        if skip_materials:
            blank_materials = True

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
                it = self.ObjectData[ObjectType.Stream].items()
                pbar = tqdm(it, desc="Processing stream objects") if self._verbose else it
                for (name, path), trs_mat_list in pbar:
                    drm_data = self._archive.get_from_filename(fr"streamgroups\{path}.drm")
                    drm = DRM()
                    drm.deserialize(drm_data)

                    for sec in drm.Sections:
                        # specifying the section number is important here -
                        # there are multiple RT sections in a single streamobject DRM
                        file_name = f"{name}_" + f"{sec.Header.SecId:x}".rjust(8, '0')
                        for idx, trs_mat in enumerate(trs_mat_list):
                            if idx == 0:
                                self._read_section_data(rm_section=sec,
                                                        trs_mat=trs_mat,
                                                        folder="stream",
                                                        file_name=file_name + ".gltf",
                                                        dest=dest,
                                                        blank_materials=blank_materials,
                                                        skip_materials=skip_materials,
                                                        )
                            write_to_dir(file_name, trs_mat)

            # external IMFs
            if ObjectType.EXT_IMF in self.ObjectData:
                it = self.ObjectData[ObjectType.EXT_IMF].items()
                pbar = tqdm(it, desc="Processing external IMFs") if self._verbose else it
                for imf_path, trs_mat_list in pbar:
                    imf_name = Path(imf_path).stem

                    if self._verbose:
                        pbar.set_description(f"Processing {imf_name}")

                    drm_data = self._archive.get_from_filename(imf_path)
                    drm = DRM()
                    drm.deserialize(drm_data)
                    for sec in drm.Sections:

                        for idx, trs_mat in enumerate(trs_mat_list):
                            if idx == 0:
                                self._read_section_data(rm_section=sec,
                                                        folder="imf_ext",
                                                        file_name=f"{imf_name}.gltf",
                                                        dest=dest,
                                                        blank_materials=blank_materials,
                                                        skip_materials=skip_materials,
                                                        )
                            write_to_dir(imf_name, trs_mat)

            # objects
            if ObjectType.OBJ in self.ObjectData:
                it = self.ObjectData[ObjectType.OBJ].items()
                pbar = tqdm(it, desc="Processing OBJs") if self._verbose else it
                for obj_name, trs_mat_list in pbar:

                    if self._verbose:
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
                                                        file_name=f"{obj_name}.gltf",
                                                        dest=dest,
                                                        blank_materials=blank_materials,
                                                        skip_materials=skip_materials,
                                                        )
                            write_to_dir(obj_name, trs_mat)

        # internal IMFs
        if ObjectType.IMF in self.ObjectData:
            it = self.ObjectData[ObjectType.IMF].items()
            pbar = tqdm(it, desc="Processing internal IMFs") if self._verbose else it
            for rm_id, trs_mat_list in pbar:
                for idx, trs_mat in enumerate(trs_mat_list):
                    rm_sec = self.lookup_section(SectionType.RenderMesh, rm_id)
                    file_name = "RenderModel_" + f"{rm_id:x}".rjust(8, '0')

                    if idx == 0:
                        self._read_section_data(rm_section=rm_sec,
                                                folder="imf_int",
                                                file_name=file_name + ".gltf",
                                                dest=dest,
                                                blank_materials=blank_materials,
                                                skip_materials=skip_materials,
                                                )
                    write_to_dir(file_name, trs_mat)

        # cell data
        if ObjectType.Cell in self.ObjectData:
            # TODO: check in the case of DRMs with many cells - possible collisions?
            it = self.ObjectData[ObjectType.Cell].items()
            pbar = tqdm(it, desc="Processing cells") if self._verbose else it
            for (cell_name, sec_id), trs_mat_list in pbar:
                sanitized_cell_name = cell_name.replace('|', '_')
                for idx, trs_mat in enumerate(trs_mat_list):
                    rm_sec = self.lookup_section(SectionType.RenderMesh, sec_id)

                    if idx == 0:
                        self._read_section_data(rm_section=rm_sec,
                                                folder="cell",
                                                file_name=f"{sanitized_cell_name}.gltf",
                                                dest=dest,
                                                blank_materials=blank_materials,
                                                skip_materials=skip_materials,
                                                )
                    write_to_dir(sanitized_cell_name, trs_mat)

        # occlusion
        if ObjectType.Occlusion in self.ObjectData:
            it = self.ObjectData[ObjectType.Occlusion].items()
            pbar = tqdm(it, desc="Processing occlusion") if self._verbose else it
            for sec_id, trs_mat_list in pbar:
                for idx, trs_mat in enumerate(trs_mat_list):
                    rm_sec = self.lookup_section(SectionType.RenderMesh, sec_id)
                    file_name = "RenderModel_" + f"{sec_id:x}".rjust(8, '0')

                    if idx == 0:
                        self._read_section_data(rm_section=rm_sec,
                                                folder="occlusion",
                                                file_name=file_name + ".gltf",
                                                dest=dest,
                                                blank_materials=blank_materials,
                                                skip_materials=skip_materials,
                                                )
                    write_to_dir(file_name, trs_mat)

        merge_single(
            output_path=dest,
            location_table=location_dir,
            split_objects_to_separate_node=self._split_objects,
            translation=self._translation,
            scale=self._scale,
            rotation=self._rotation,
            trs_matrix=self._trs_mat,
            verbose=self._verbose,
        )
