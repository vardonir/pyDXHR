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

breakpoint()
