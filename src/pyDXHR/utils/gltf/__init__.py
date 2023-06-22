from .build import build_gltf as build
from .net import GLTFDiGraph
from .merge import merge_single_node_gltf as merge_single
from .merge import merge_multinode_gltf as merge_multiple

# import pygltflib as gl
# from typing import Optional
#
#
# def convert_image_path_to_gltf_buffer(image_path):
#     import base64
#     from pathlib import Path
#
#     buffer = gl.Buffer()
#
#     with open(image_path, 'rb') as f:
#         byte_data = f.read()
#         encoded = base64.b64encode(byte_data)
#
#     buffer.uri = 'data:image/png;base64,{}'.format(encoded)
#     buffer.byteLength = len(byte_data)
#     buffer.name = Path(image_path).stem
#
#     return buffer


def black_image_as_gltf_buffer():
    import pygltflib as gl
    import base64
    img = generate_black_image()
    encoded = base64.b64encode(img)

    return gl.Buffer(
        uri='data:application/octet-stream;base64,{}'.format(str(encoded).split("'")[1]),
        byteLength=len(img)
    )

    # bufferView = gl.BufferView(
    #     name="dummyblack",
    #     buffer=0,
    # )
    #
    # im = gl.Image(
    #     name="dummyblack",
    #     bufferView=0,
    #     mimeType="image/png",
    # )


def generate_black_image():
    from PIL import Image
    import io
    import numpy as np

    image = np.zeros((4, 4, 4), dtype=np.uint8)
    image[..., 3] = 255

    image = Image.fromarray(image)

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# def empty_pbr(empty_tex_index: int):
#     tf = gl.TextureInfo(
#         index=empty_tex_index,
#         texCoord=0
#     )
#
#     return gl.PbrMetallicRoughness(
#         metallicFactor=0.0,
#         roughnessFactor=1.0,
#         baseColorFactor=[1.0, 1.0, 1.0, 1.0],
#         baseColorTexture=tf,
#         metallicRoughnessTexture=tf
#     )
#
#
# def empty_normal(empty_tex_index: int):
#     return gl.NormalMaterialTexture(
#         index=empty_tex_index,
#         texCoord=0,
#         scale=1.0
#     )
#
#
# def empty_occlusion(empty_tex_index: int):
#     return gl.OcclusionTextureInfo(
#         index=empty_tex_index,
#         texCoord=0,
#         strength=1.0
#     )
#
#
# def modify_empty_emissive(
#         mat: gl.Material,
#         empty_tex_index: Optional[int] = None
# ):
#     mat.emissiveTexture = gl.TextureInfo(
#         index=empty_tex_index,
#         texCoord=0
#     )
#
#     mat.emissiveFactor = [0.0, 0.0, 0.0]
