# Replacing Textures

TODO: Instructions are WIP

- Extract the model and textures using the DRM to GLTF exporter
- Replace the textures with your own, make sure to keep the same file names

Replacement textures:
- Use the same compression as the original texture
- Dimensions don't have to be the same
- In GIMP, make sure to use "Generate Mipmaps"
- Save as DDS

- Calculate the file hash of the DRM that you want to replace. You can use [this one from the cdcEngine Research page](https://cdcengine.re/crc32/), just enter the filename (with the `pc-w` prefix), make sure that the folders are backslashes

- Run the texture replacement script (TODO: finalize the script)

Notes:
- you are not restricted to the original size and dimensions of the image
- not yet tested on non-DXT1 textures
- 