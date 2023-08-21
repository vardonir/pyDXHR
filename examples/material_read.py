from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM import DRM
from pyDXHR.DRM.Section import Material

# Assumes that you have the PC Director's Cut edition specified in env
bf = Bigfile.from_env()
# bf.unpack_from = 'cache'
bf.open()

simple_rendermodel = "imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_sarif_office\sarif_office_fire_a\sarif_office_fire_a.drm"  # noqa
simple_renderterrain = "streamgroups\det_adam_apt_a_all.drm"  # noqa

render_mesh_drm = DRM.from_bigfile(simple_renderterrain, bf)
render_mesh_drm.open()

mat_list = Material.from_drm(render_mesh_drm)

for mat in mat_list:
    mat.read()

    breakpoint()
