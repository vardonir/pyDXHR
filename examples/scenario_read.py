from pyDXHR.Bigfile import Bigfile, write_new_bigfile
from pyDXHR.DRM import ScenarioDatabase
from pyDXHR.DRM.scenario import ScenarioDRM

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
bf.open()

scn_db = ScenarioDatabase.from_bigfile(bf)
scn_db.open()

# found dtp data subtype 16 and 21 in the scenario DRMs
# scn = ScenarioDRM.from_bigfile('s_scn_det02_waynehaas_nonhostile_det_adam_apt_a', bf)
scn = ScenarioDRM.from_bigfile('s_scn_det01_sq02_cassandra_end_det_adam_apt_a', bf)
scn.open()

breakpoint()
