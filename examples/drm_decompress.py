from pyDXHR.Bigfile import Bigfile
from pyDXHR import DRM

# Decompress from Bigfile specified in .env
# Assumes that you have the PC Director's Cut edition specified in env
bf = Bigfile.from_env()
bf.open()
compressed_data = bf.read(0xAB0AD4A3)
decompressed_data = DRM.decompress(compressed_data)
print(compressed_data[0:10])
print(decompressed_data[0:10])

# Decompress from previously-extracted CDRM file in path
with open("../tests/AB0AD4A3.drm", 'rb') as f:
    compressed_data = f.read()
    decompressed_data = DRM.decompress(compressed_data)
print(compressed_data[0:10])
print(decompressed_data[0:10])
