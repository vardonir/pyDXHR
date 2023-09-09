dx9 = r"shaderlibs\2d_1cb1e3d7d02c5fe5_dx9"
dx11 = r"shaderlibs\2d_1cb1e3d7d02c5fe5_dx11"

from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM import DRM

bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
bf.open()

shader_lib = DRM.from_bigfile(dx11, bf)
shader_lib.open()

breakpoint()
