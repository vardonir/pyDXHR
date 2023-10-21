from pyDXHR.Bigfile import Bigfile, write_new_bigfile
from pyDXHR.locals import Locals
from pyDXHR.DRM.Database.emails import EmailDatabase
from pyDXHR.DRM.Database.ireader import IReaderDatabase

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
bf.open()

locals_bin = Locals.from_bigfile(bf)
locals_bin.open()

# basic find-and-replace modification
intro_text = r"Welcome to Deus Ex: Human Revolution - Director's Cut. For information and updates, visit www.DeusEx.com or connect to the Internet."  # noqa
replacement_text = "hello world! -Vardonir"

locals_bin.modify_text(original=intro_text, replacement=replacement_text)

# then some emails
mail_db = EmailDatabase.from_bigfile(bf)
mail_db.set_locals_bin(locals_bin)
mail_db.open()

# email from cassandra
mail_db[32047].modify(
    from_="Sample edit sender",
    to="Sample edit recipient",
    subject="Sample edit subject",
    body="Sample edit text",
)

# email from sarif
mail_db[32048].modify(
    from_="Sample edit sender",
    to="Sample edit recipient",
    subject="Sample edit subject",
    body="Sample edit text",
)

locals_bin = mail_db.write()

ir_db = IReaderDatabase.from_bigfile(bf)
ir_db.set_locals_bin(locals_bin)
ir_db.open()

# and also some ebooks
# this one is the patient X ebook on megan's couch
ir_db[32051].modify(
    title="Sample edit title",
    author="Sample edit author",
    body="Sample edit text",
)

locals_bin = ir_db.write()
entry = locals_bin.write()
out_000 = write_new_bigfile([entry], source_bigfile=bf)

mods_folder = r"F:\Games\Deus Ex HRDC\mods"
with open(mods_folder + r"/locals_multimod.000", "wb") as ff:
    ff.write(out_000[0])
