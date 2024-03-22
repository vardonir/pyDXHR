"""
Class for reading the unit DRM subtype
"""
import numpy as np
from typing import Optional, List, Dict, Tuple
from tqdm import trange
from scipy.spatial.transform import Rotation
import struct
from pyDXHR.DRM import DRM, Section
from pyDXHR.DRM.resolver import Reference
from pyDXHR import SectionType
import os
from dotenv import load_dotenv

load_dotenv()


class UnitDRM(DRM):
    _identity_trs = np.eye(4).astype(float)

    def __init__(self):
        super().__init__()
        self.is_masterunit: bool = False
        self.linked_drm_list: List[str] = []
        self.streamgroup_map: Dict[Tuple[str, str], List[np.ndarray]] = {}
        self.cell_map: Dict[Tuple[str, int], List[np.ndarray]] = {}
        self.cell_section_data: Dict[Tuple[str, int], Section] = {}
        self.occlusion_map: Dict[int, List[np.ndarray]] = {}
        self.obj_map: Dict[int, List[np.ndarray]] = {}
        self.int_imf_map: Dict[int, List[np.ndarray]] = {}
        self.int_imf_section_data: Dict[Tuple[str, int], Section] = {}
        self.ext_imf_map: Dict[str, List[np.ndarray]] = {}

        self._obj_ref: Optional[Reference] = None
        self._obj_count: Optional[int] = None
        self._imf_ref: Optional[Reference] = None
        self._imf_count: Optional[int] = None

    def read_objects(self) -> Dict[int, List[np.ndarray]]:
        if not self._is_open:
            self.open()

        if self._obj_ref is None:
            return {}

        endian = self._obj_ref.section.header.endian
        obj_indices = {}

        if bool(os.getenv("verbose", False)):
            pbar = trange(self._obj_count, desc="Reading OBJ data")
        else:
            pbar = range(self._obj_count)
        for i in pbar:
            (index,) = struct.unpack_from(
                f"{endian}H",
                self._obj_ref.section.data,
                0x30 + self._obj_ref.offset + i * 0x70,
            )

            trs_compact = np.frombuffer(
                self._obj_ref.section.data,
                dtype=np.dtype(np.float32).newbyteorder(endian),
                count=12,
                offset=self._obj_ref.offset + i * 0x70,
            )
            rot = trs_compact[0:3]
            pos = trs_compact[4:7]
            scl = trs_compact[8:11]

            # see: https://en.wikipedia.org/wiki/Euler_angles#Conventions_by_intrinsic_rotations
            #      https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.from_euler.html
            rot_as_matrix = Rotation.from_euler("XYZ", rot, degrees=False).as_matrix().T

            trs_mat = np.zeros((4, 4))
            trs_mat[0:3, 0:3] = np.diag(scl)
            trs_mat[0:3, 0:3] = rot_as_matrix
            trs_mat[-1, :] = np.array(list(pos) + [1])
            trs_mat = trs_mat.T

            if index not in obj_indices:
                obj_indices[index] = []

            obj_indices[index].append(trs_mat)

        self.obj_map = obj_indices

    def read_imfs(self) -> Dict[str | int, List[np.ndarray]]:
        """
        Process IMF references. Will process both internal and external IMFs regardless of input kwargs.
        External IMFs only get the file names + TRS matrix, whereas internal IMFs get the section ID + TRS matrix.
        Processing external IMFs require an attached archive.
        """
        if not self._is_open:
            self.open()
        if not self._imf_ref:
            return {}

        ext_imf_dict: Dict[str, List[np.ndarray]] = {}
        int_imf_dict: Dict[int, List[np.ndarray]] = {}
        endian = self._imf_ref.section.header.endian

        if bool(os.getenv("verbose", False)):
            pbar = trange(self._imf_count, desc="Reading IMF data")
        else:
            pbar = range(self._imf_count)
        for i in pbar:
            # trs_mat = self._imf_ref.access("16f", i * 0x90)
            trs_mat_np = np.frombuffer(
                self._imf_ref.section.data,
                dtype=np.dtype(np.float32).newbyteorder(endian),
                count=16,
                offset=self._imf_ref.offset + i * 0x90,
            )

            # trs_mat = np.asarray(trs_mat).reshape((4, 4)).T
            trs_mat = np.asarray(trs_mat_np).reshape((4, 4)).T
            # if self._round:
            #     trs_mat = trs_mat.round(self._round)

            dtpid = self._imf_ref.access("I", i * 0x90 + 0x48)
            fname_ref = self._imf_ref.deref(0x4C + i * 0x90)

            if dtpid and not fname_ref:  # IMFs embedded in the file
                dtp_imf_ref = Reference.from_section_type(
                    drm_or_section_list=self.sections,
                    section_type=SectionType.dtpdata,
                    section_id=dtpid,
                )
                rm_imf_ref = dtp_imf_ref.deref(0x4)
                rm_sec = rm_imf_ref.section

                if rm_sec.header.section_id not in int_imf_dict:
                    int_imf_dict[rm_sec.header.section_id] = []
                int_imf_dict[rm_sec.header.section_id].append(trs_mat)
                self.int_imf_section_data[rm_sec.header.section_id] = rm_sec
            elif not fname_ref:
                pass
            else:  # IMFs elsewhere
                fname = fname_ref.access_string()
                if fname not in ext_imf_dict:
                    ext_imf_dict[fname] = []

                ext_imf_dict[fname].append(trs_mat)

        self.ext_imf_map = ext_imf_dict
        self.int_imf_map = int_imf_dict

    def open(self):
        """
        Read the DRM's references to other sections.
        Since reading the data for the objects and IMF sometimes takes a while, these are
        kept in separate functions, but it's not necessary to call `open()` if you'll run
        `read_objects()` or `read_imfs()` anyway.
        """
        super().open()

        if self.name is not None and self.name.endswith("masterunit.drm"):
            self.is_masterunit = True

        unit_ref = Reference.from_root(self)

        # region ref_sub0
        if bool(os.getenv("verbose", False)):
            print("Reading ref_sub0")

        ref_sub0 = unit_ref.deref(0)
        ref_linked = ref_sub0.deref(0x4)
        if ref_linked:
            len_linked = ref_sub0.access("H", 0x2)
            self.linked_drm_list = [
                ref_linked.access_string(0x100 * i, "utf-8") for i in range(len_linked)
            ]

        ref_collision = ref_sub0.deref(0x18)
        if ref_collision:
            len_collision = ref_sub0.access("I", 0x14)
            # TODO
        # endregion

        # region ref_sub30
        if bool(os.getenv("verbose", False)):
            print("Reading ref_sub30")

        sub30_ref = unit_ref.deref(0x30)
        if sub30_ref:
            self._obj_ref = sub30_ref.deref(0x18)
            self._obj_count = sub30_ref.access("I", 0x14)

            self._imf_ref = sub30_ref.deref(0xA8)
            self._imf_count = sub30_ref.access("I", 0xA4)
        # endregion

        # region ref_sub50
        if bool(os.getenv("verbose", False)):
            print("Reading ref_sub50")

        sub50_ref = unit_ref.deref(0x50)  # CellGroupData
        if sub50_ref:
            # Incomplete?
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
            ref_streamgroup = sub50_ref.deref(0xC)  # CellStreamGroupData*
            sub50_14 = sub50_ref.deref(0x14)  # CellData*[]
            sub50_18 = sub50_ref.deref(0x18)  # CellStreamData (void terrain)
            # sub50_1c = sub50_ref.deref(0x1c)  # CellStreamData (exterior terrain)

            if sub50_0:
                # struct CellGroupDataHeader { // 50
                # 	uint32_t numTotalCells; // 0
                # 	uint32_t numToplevelCells; // 4
                # 	uint32_t numBSPNodes; // 8
                # 	uint32_t numStreamGroups; // C
                # 	uint32_t numSymbols; // 10
                # 	uint32_t numPortalSymbols; // 14
                # 	uint32_t symbolTableSize; // 18
                # };
                if ref_streamgroup:
                    len_streamgroups = sub50_0.access("I", 0xC)

                    for i in range(len_streamgroups):
                        streamgroup_ref = ref_streamgroup.add(i * 0x14)
                        streamgroup_name = streamgroup_ref.deref(0x0)
                        streamgroup_path = streamgroup_ref.deref(0xC)

                        if streamgroup_path:
                            streamgroup_name = streamgroup_name.access_string()
                            streamgroup_path = streamgroup_path.access_string()
                            key = (streamgroup_name.lower(), streamgroup_path.lower())

                            # try:
                            #     streamgroup_name = streamgroup_name.access_string()
                            #     streamgroup_path = streamgroup_path.access_string()
                            #     key = (streamgroup_name.lower(), streamgroup_path.lower())
                            # except AttributeError:
                            #     continue
                            # else:
                            if key not in self.streamgroup_map:
                                self.streamgroup_map[key] = []

                            self.streamgroup_map[key].append(self._identity_trs)

                if sub50_18:
                    # sub50_18_4 = sub50_18.deref(4)  # ???
                    len_cells = sub50_0.access(f"L")

                    # sub50_18.deref(0x20).get_string()  # a bunch of strings ???

                    if sub50_14:
                        cell_names = []
                        ref_list_cell = []
                        ref_list_occlusion = []
                        for i in range(len_cells):
                            cell = sub50_14.deref(4 * i)
                            cell_sub0 = cell.deref(0)
                            try:
                                cell_sub4 = cell.deref(0x4)
                                cell_sub4_0 = cell_sub4.deref(0x0)
                            except AttributeError:
                                cell_sub4_0 = None

                            cell_sub20 = cell.deref(0x20)
                            cell_name = cell_sub0.deref(0x0).access_string()
                            cell_names.append(cell_name)

                            if cell_sub4_0:
                                ref_list_cell.append((cell_sub4_0, cell_name))
                                self.cell_section_data |= {
                                    (
                                        cell_name,
                                        cell.section.header.section_id,
                                    ): cell_sub4_0.section
                                }

                            ref_list_occlusion.append(cell_sub20)

                        if ref_list_cell:
                            cell: Reference
                            cell_name: str

                            self.cell_map = {
                                (cell_name, cell.section.header.section_id): [
                                    self._identity_trs
                                ]
                                for cell, cell_name in ref_list_cell
                            }

                        if ref_list_occlusion:
                            ref: Reference

                            self.occlusion_map = {
                                ref.section.header.section_id: [self._identity_trs]
                                for ref in ref_list_occlusion
                            }
