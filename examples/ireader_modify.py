from pyDXHR.Bigfile import Bigfile, write_new_bigfile
from pyDXHR.DRM import iReaderDatabase

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
bf.open()

ir_db = iReaderDatabase.from_bigfile(bf)
ir_db.open()

breakpoint()
