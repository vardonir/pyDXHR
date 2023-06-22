from pyDXHR.utils.MeshData import *


def build(mesh_data: MeshData, **kwargs):
    import trimesh

    meshes = []

    for vb_idx, vb in mesh_data.VertexBuffers.items():

        normals = vb.get(VertexSemantic.Normal)
        if normals is None:
            normals = vb.get(VertexSemantic.Normal2)
            if normals is None:
                pass

        tm = trimesh.Trimesh(
            vertices=vb.get(VertexSemantic.Position),
            vertex_normals=normals,
            visual=None
        )

        breakpoint()


if __name__ == "__main__":
    from pyDXHR.cdcEngine.Archive import Archive
    from pyDXHR.cdcEngine.Sections import RenderMesh
    from pyDXHR.cdcEngine.DRM.DRMFile import DRM

    arc = Archive()
    arc.deserialize_from_env()
    # arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHR 1.0.499.0 beta\BIGFILE.000")
    # arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHRDCPS3\CACHE.000")
    # arc.deserialize_from_file(r"F:\Games\Deus Ex HRDC\BIGFILE.000")

    file = r"imf\imf_props\imf_furniture\imf_shelves\sarif_office_bookshelf_a\sarif_office_bookshelf_a.drm"
    drm_inst = DRM()
    drm_inst.deserialize(arc.get_from_filename(file))
    rm_sec = RenderMesh.deserialize_drm(drm_inst)

    for s in rm_sec:
        out = s.to_obj()

        breakpoint()
