from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM

arc = Archive()
arc.deserialize_from_env()
# arc.deserialize_from_file(r"F:\Game_Rips\deus-ex-human-revolution\raw\archive\PC_DC\BIGFILE.000")

# one_track_mind = "det_city_sarif.drm"  # the one that matters
# hehe_its_a_track_get_it = "det_city_tunnel1.drm"  # it's a track - useful small unit for testing
# just_a_dipshit_from_detroit = "det_adam_apt_c.drm"  # a lot of everything, but is kinda big
# im_a_fucking_corpo_shill = "det_sarif_industries.drm"  # the one that really matters, but you keep stalling it
file = "det_city_tunnel1.drm"
pc_data = arc.get_from_filename(file)


# read as unit
pc_drm = UnitDRM(
    uniform_scale=0.002,
    z_up=True
)
pc_drm.deserialize(
    pc_data,
    archive=arc,
    split_by_occlusion=True,

    imf=False,
    skip_ext_imf=True,
    stream=False,
    obj=False,
    occlusion=False,
    cell=False,
    # collision=False,
)

cm = pc_drm.CollisionMesh[0]
gltf = cm.to_gltf(scale=[0.002, 0.002, 0.002], as_bytes=True)

import trimesh
import trimesh.intersections
import trimesh.interfaces
from io import BytesIO
import numpy as np

mesh = trimesh.load(BytesIO(gltf), file_type="glb", force="mesh")
geom = mesh.process()

bbox = geom.bounding_box_oriented
center = np.array(bbox.transform).T[3, :3]
linspace = np.linspace(*geom.bounds[:, 2], 10)

for idx, (st, ed) in enumerate(zip(linspace[0:], linspace[1:])):
    sliced_mesh = trimesh.intersections.slice_mesh_plane(
        mesh=geom,
        plane_normal=[0,0,1],
        plane_origin=[center[0], center[1], st],
        cap=False
    )

    sliced_mesh_2 = trimesh.intersections.slice_mesh_plane(
        mesh=sliced_mesh,
        plane_normal=[0,0,-1],
        plane_origin=[center[0], center[1], ed],
        cap=False
    )

    print(sliced_mesh_2.is_convex)
    export_blob = sliced_mesh_2.export(file_type="glb")

    breakpoint()

    import pygltflib as gl
    gl.GLTF2().load_from_bytes(export_blob).save(f"F:\Projects\pyDXHR\output\collision_{idx}.gltf")

# breakpoint()

# gltf_trimesh.show(flags={'wireframe': True}, background=[0, 0, 0, 0])
