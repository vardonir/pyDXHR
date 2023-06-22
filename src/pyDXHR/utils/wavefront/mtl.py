import trimesh.visual
import trimesh.creation
import os
from PIL import Image

texture_library = os.getenv("PYDXHR_TEXLIB")


def cdcMaterial_to_WavefrontMaterial(cdc_mat, double_sided=False):
    base_color_texture = Image.open(cdc_mat.Diffuse[0][1]) if len(cdc_mat.Diffuse) == 1 else None
    specular_texture = Image.open(cdc_mat.Specular[0][1]) if len(cdc_mat.Specular) == 1 else None
    normal_texture = Image.open(cdc_mat.Normal[0][1]) if len(cdc_mat.Normal) == 1 else None

    pbr_mat = trimesh.visual.material.PBRMaterial(
        name=hex(cdc_mat.ID).replace("0x", ""),
        # emissiveFactor=(1.0, 1.0, 1.0),
        # emissiveTexture=None,
        # baseColorFactor=None,
        metallicFactor=0.0,
        roughnessFactor=1.0,
        normalTexture=normal_texture,
        occlusionTexture=None,
        baseColorTexture=base_color_texture,
        metallicRoughnessTexture=specular_texture,
        doubleSided=double_sided,
        alphaMode="MASK" if cdc_mat.HasAlpha else "OPAQUE",
        alphaCutoff=0.5 if cdc_mat.HasAlpha else 1,
    )

    visual = trimesh.visual.TextureVisuals(material=pbr_mat)
    box = trimesh.creation.box(extents=(10, 10, 10), visual=visual)
    # box.show()

    breakpoint()


if __name__ == "__main__":
    from pyDXHR.cdcEngine.Archive import Archive
    from pyDXHR.cdcEngine.Sections import Material
    from pyDXHR.cdcEngine.DRM.DRMFile import DRM

    arc = Archive()
    arc.deserialize_from_env()
    # arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHR 1.0.499.0 beta\BIGFILE.000")
    # arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHRDCPS3\CACHE.000")
    # arc.deserialize_from_file(r"F:\Games\Deus Ex HRDC\BIGFILE.000")

    file = r"imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_atrium\adam_office_a\adam_office_a.drm"
    drm_inst = DRM()
    drm_inst.deserialize(arc.get_from_filename(file))
    mtlsec_set = Material.deserialize_drm(drm_inst)

    for mtlsec in mtlsec_set:
        mtlsec.to_wavefront_mtl()

    breakpoint()
