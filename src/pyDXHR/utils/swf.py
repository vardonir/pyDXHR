def get_ffdec_path():
    import os
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv()

    external = os.getenv('PYDXHR_EXTERNAL_DEPENDENCIES')

    return str(Path(external) / "ffdec_18.4.1" / "ffdec.jar")


def download():
    # TODO
    pass


def export(cfx_data, export_type: str = "image"):
    import tempfile
    import subprocess
    import os
    from glob import glob
    from pathlib import Path
    import shutil

    out_data = []
    in_fd, in_path = tempfile.mkstemp(suffix=".swf")
    out_dir = os.path.join(tempfile.gettempdir(), "pyDXHR", "swf")
    try:
        with os.fdopen(in_fd, 'wb') as in_tf:
            in_tf.write(cfx_data)

            result = subprocess.run(['java', '-jar', get_ffdec_path(), '-export', export_type, out_dir, in_path],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode == 0:
                out_data = glob(f"{out_dir}/*.png")
            else:
                raise Exception(result.stdout)
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)
        os.remove(in_path)

    as_dict = {int(Path(i).stem.split("_")[0]): "_".join(Path(i).stem.split("_")[1:]).replace("%2F", "/") + ".tga" for i in out_data}
    return sorted((idx, item) for idx, item in as_dict.items())


def decompress_cfx(cfx_data):
    import tempfile
    import subprocess
    import os

    out_data = b""
    in_fd, in_path = tempfile.mkstemp(suffix=".swf")
    out_fd, out_path = tempfile.mkstemp(suffix=".swf")
    try:
        with os.fdopen(in_fd, 'wb') as in_tf:
            in_tf.write(cfx_data)

            result = subprocess.run(['java', '-jar', get_ffdec_path(), '-decompress', in_path, out_path],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        with os.fdopen(out_fd, 'rb') as out_tf:
            out_data = out_tf.read()

    finally:
        os.remove(in_path)
        os.remove(out_path)

    if result.returncode == 0:
        return out_data
    else:
        raise Exception(result.stdout)


if __name__ == "__main__":
    import subprocess
    result = subprocess.run(['java', '-jar', get_ffdec_path(), '--help'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    breakpoint()
