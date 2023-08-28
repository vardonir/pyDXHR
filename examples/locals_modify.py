from pyDXHR.Bigfile import Bigfile, write_new_bigfile
from pyDXHR.locals import Locals

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
bf.open()

locals_instance = Locals.from_bigfile(bf)
locals_instance.open()

intro_text = r"Welcome to Deus Ex: Human Revolution - Director's Cut. For information and updates, visit www.DeusEx.com or connect to the Internet."  # noqa
replacement_text = "hello world! -Vardonir"

locals_instance.modify_text(original_text=intro_text, replacement_text=replacement_text)
replacement_entry = locals_instance.write()

new_bf = write_new_bigfile([replacement_entry], source_bigfile=bf)

breakpoint()
