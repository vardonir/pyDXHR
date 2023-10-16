# Development

## Python Dependencies

* Python 3.10
* Numpy
* fastcrc
* [kaitaistruct](https://kaitai.io/) - The python-generated code is part of the repo, and the raw KSY files are also included.
* scipy - for handling rotations
* black and pylint

For the exporters:

* Textures: Pillow (conversion from DDS to PNG/TGA)
* Models: [pygltflib](https://gitlab.com/dodgyville/pygltflib) 
* Audio: [vgmstream](https://github.com/vgmstream/vgmstream) - used as a CLI tool with subprocess
* Cinematics: [WannaCRI](https://github.com/donmai-me/WannaCRI)

Demos:

* Jupyter/ipynb
* Trimesh + pyglet for the 3D models

## Shell scripts

- `kaitai-struct-compiler --target python --outdir .\pyDXHR\generated\ --python-package pyDXHR .\ksy\*.ksy` - generate the python code from the KSY files
- `sphinx-build -b html sphinx_docs/ docs -E` - generate the documentation
- `black --exclude="generated/*" ./pyDXHR/` - format the code

## Data?

Getting the data for the PC version is straightforward, just go to whereever you installed the game. For the console versions:

WiiU: Use [cDecrypt](https://github.com/VitaSmith/cdecrypt)

Xbox 360: Follow the instructions for [extract-iso](https://github.com/XboxDev/extract-xiso). You can extract the two discs of the DC version separately.

PS3: Unpack the ISO like a ZIP file.
