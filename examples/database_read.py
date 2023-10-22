from pyDXHR.Bigfile import Bigfile
bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
bf.open()

# from pyDXHR.DRM.Database.objective import ObjectiveDatabase
# obj_db = ObjectiveDatabase.from_bigfile(bf)
# obj_db.open()

from pyDXHR.DRM.Database.pickup import PickupDatabase
pick_db = PickupDatabase.from_bigfile(bf)
pick_db.open()

breakpoint()
