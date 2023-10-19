""" Sample code to modify the contents of the ebooks/ireaders in-game """

from pyDXHR.Bigfile import Bigfile, write_new_bigfile
from pyDXHR.DRM.Database.ireader import IReaderDatabase

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
bf.open()

ir_db = IReaderDatabase.from_bigfile(bf)
ir_db.open()

# let's modify these two ebooks for example:
# 30585 The Nature of Neuroplasticity
# 30586 Sarif Industries: Rising to Tomorrow
# both of these could be found at the 2nd floor in the SI HQ

ebook_30585 = ir_db[30585]
ebook_30586 = ir_db[30586]

ebook_30585.modify(
    title="Sample edit title",
    author="Sample edit author",
    body="Sample edit text",
)

ebook_30586.modify(
    title="Sample edit title",
    author="Sample edit author",
    body="Sample edit text",
)

local_bin = ir_db.write()
archive_entry = local_bin.write()
out_000 = write_new_bigfile([archive_entry], bf)

mods_folder = r"F:\Games\Deus Ex HRDC\mods"
with open(mods_folder + r"/ebook_mod.000", "wb") as ff:
    ff.write(out_000[0])

breakpoint()
