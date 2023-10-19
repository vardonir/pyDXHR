from pyDXHR.Bigfile import Bigfile, write_new_bigfile
from pyDXHR.locals import Locals

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
bf.open()

locals_instance = Locals.from_bigfile(bf)
locals_instance.open()

intro_text = r"Welcome to Deus Ex: Human Revolution - Director's Cut. For information and updates, visit www.DeusEx.com or connect to the Internet."  # noqa
replacement_text = "hello world! -Vardonir"

locals_instance.modify_text(original=intro_text, replacement=replacement_text)
replacement_entry = locals_instance.write()

out_000 = write_new_bigfile([replacement_entry], source_bigfile=bf)

mods_folder = r"F:\Games\Deus Ex HRDC\mods"
with open(mods_folder + r"/hello_world.000", "wb") as ff:
    ff.write(out_000[0])
