from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM.Database.ireader import IReaderDatabase

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
bf.open()

ir_db = IReaderDatabase.from_bigfile(bf)
ir_db.open()

# get a list of all the ireaders in the database
with open("ebook_data.txt", "w", encoding='utf-8') as ff:
    for key in ir_db.data:
        title = ir_db[key].ebook_title
        author = ir_db[key].ebook_author
        body = ir_db[key].ebook_body

        ff.write(f"{title}\n")

        if author is not None:
            ff.write(f"{author}\n")

        ff.write(f"{body}\n\n\n")
