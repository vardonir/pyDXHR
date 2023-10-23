import tempfile
from pathlib import Path
from wannacri.usm.usm import Usm
from pyDXHR.Bigfile import Bigfile


def demux(
        bigfile: Bigfile,
        usm_file_path: str,
        save_to: Path | str
):
    if Path(usm_file_path).suffix == ".usm":
        byte_data = bigfile.read_data_by_name(usm_file_path)

        tf_usm = tempfile.NamedTemporaryFile(suffix=".usm", delete=False)
        tf_usm.write(byte_data)
        tf_usm.seek(0)

        usm_file = Usm.open(tf_usm.name)
        video_data, audio_data = usm_file.demux(Path(usm_file_path).name, folder_name=save_to)

    else:
        raise FileNotFoundError
