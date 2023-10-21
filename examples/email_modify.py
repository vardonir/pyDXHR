from pyDXHR.Bigfile import Bigfile, write_new_bigfile
from pyDXHR.DRM.Database.emails import EmailDatabase


bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
bf.open()

mail_db = EmailDatabase.from_bigfile(bf)
mail_db.open()

# let's modify:
# Megan's computer:
# 32047 - Cassandra
# 32048 - Sarif
# 32049 - Diane

mail_32047 = mail_db[32047]

mail_32047.modify(
    from_="Sample edit sender",
    to="Sample edit recipient",
    subject="Sample edit subject",
    body="Sample edit text",
)

local_bin = mail_db.write()
archive_entry = local_bin.write()
out_000 = write_new_bigfile([archive_entry], bf)

mods_folder = r"F:\Games\Deus Ex HRDC\mods"
with open(mods_folder + r"/email_mod.000", "wb") as ff:
    ff.write(out_000[0])

breakpoint()
