# Entrypoints

These will be compiled as .exe files which (in theory) can be more user-friendly. A lot of this is just recreating what Gibbed already made, but these can be built and used in non-Windows platforms as well.

## Bigfile unpack
Drag-drop the Bigfile.000 file into the .exe.

Usage from commandline:
```
usage: pyDXHR Bigfile Unpacker [-h] [-o OUT] [-u] [-k] source

Unpack bigfiles from DXHR

positional arguments:
  source

options:
  -h, --help          show this help message and exit
  -o OUT, --out OUT   output directory
  -u, --skip-unknown  Skip unknown files
  -k, --skip-known    Skip known files
```

## Bigfile repack
TODO

## DRM decompress
Drag-drop the compressed DRM into the .exe. Alternatively, provide the path as an argument.

```
Usage: drm_decompress.exe <input_file>
```

## DRM section extract
TODO

## RenderMesh GLTF convert
TODO