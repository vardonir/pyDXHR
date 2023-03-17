def to_wav(mul):
    import tempfile
    import subprocess
    import os

    fd, path = tempfile.mkstemp(suffix=".fsb")
    try:
        with os.fdopen(fd, 'wb') as tf:
            tf.write(mul.Streams)

        result = subprocess.run(['..\\external\\vgmstream\\vgmstream-cli.exe', '-i', "-P", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    finally:
        os.remove(path)

    return result.stdout
