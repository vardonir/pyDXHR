from pathlib import Path
import tempfile

from pyDXHR.cdcEngine.Archive import Archive
from wannacri.usm.usm import Usm


def demux(archive: Archive, file_path: str):
    if Path(file_path).suffix == ".usm":
        byte_data = archive.get_from_filename(file_path)

        breakpoint()

    else:
        raise FileNotFoundError


if __name__ == "__main__":
    from pyDXHR.cdcEngine.Archive import Archive

    pc_dc = r"INSTALL_PATH\DXHRDC\BIGFILE.000"
    arc = Archive()
    arc.deserialize_from_file(pc_dc)

    usm_path = r"design_database\videos\cinematics\final_cinematics\cut_01_shq0_3_woundedheroreturns\dxni_115_v10-woundedheroreturns.usm"

    demux(arc, usm_path)