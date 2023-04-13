import os
from pathlib import Path
import tempfile
from typing import Optional

from pyDXHR.cdcEngine.Archive import Archive
from wannacri.usm.usm import Usm


def demux(
        archive: Archive,
        usm_file_path: str,
        folder_dest: Optional[Path | str] = None
):
    if Path(usm_file_path).suffix == ".usm":
        byte_data = archive.get_from_filename(usm_file_path)

        tf_usm = tempfile.NamedTemporaryFile(suffix=".usm", delete=False)
        tf_usm.write(byte_data)
        tf_usm.seek(0)

        temp_dir = tempfile.TemporaryDirectory()
        usm_file = Usm.open(tf_usm.name)
        video_data, audio_data = usm_file.demux(Path(usm_file_path).name, folder_name=str(temp_dir))

        # TODO: doesn't work at the moment
        # tf_usm.close()
        # os.remove(tf_usm.name)

        # breakpoint()

    else:
        raise FileNotFoundError


if __name__ == "__main__":
    from pyDXHR.cdcEngine.Archive import Archive

    pc_dc = r"C:\Users\vardo\DXHR_Research\DXHRDC\BIGFILE.000"
    arc = Archive()
    arc.deserialize_from_file(pc_dc)

    usm_path = r"design_database\videos\cinematics\final_cinematics\cut_01_shq0_3_woundedheroreturns\dxni_115_v10-woundedheroreturns.usm"

    demux(arc, usm_path)
