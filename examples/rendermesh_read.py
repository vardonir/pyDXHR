from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM import DRM
from pyDXHR.DRM.Section import RenderMesh

bf = Bigfile.from_env()
bf.open()

simple_rendermodel = "imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_sarif_office\sarif_office_fire_a\sarif_office_fire_a.drm"  # noqa
simple_renderterrain = "streamgroups\det_adam_apt_a_all.drm"  # noqa

render_mesh_drm = DRM.from_bigfile(simple_renderterrain, bf)
render_mesh_drm.open()

rm_list = RenderMesh.from_drm(render_mesh_drm)

# generate MeshData
for rm in rm_list:
    md = rm.parse_mesh_data()
    gltf = md.to_lumen_gltf(save_to=r"C:\Users\vardo\Documents\pyDXHR\playground\mesh\lumen.gltf")
breakpoint()
