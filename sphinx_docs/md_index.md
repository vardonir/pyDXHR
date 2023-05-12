# pyDXHR Documentation


Python-based tools for data exploration and extraction of Deus Ex Human Revolution, intended for use in another project of mine: [Project SI-X](https://six.vardonir.com/)

Although I went a bit too far and somehow managed to make basic mod tools? 

Documentation be here, when I feel like writing it + some notes on stuff I've found while digging through the files.

There was an attempt to make the docs look and feel like a professionally-written document. An attempt. I didn't succeed. 

## Dependencies

* Python 3.10
* Numpy
* fastcrc
* [kaitaistruct](https://kaitai.io/) - The python-generated code is part of the repo, but the raw KSY files are also included.
* scipy - mostly for handling rotations

For the exporters:

* Textures: Pillow
* Models: [pygltflib](https://gitlab.com/dodgyville/pygltflib) 
* Audio: [vgmstream](https://github.com/vgmstream/vgmstream) - used as a CLI tool
* Cinematics: [WannaCRI](https://github.com/donmai-me/WannaCRI)

Demos:

* Jupyter/ipynb
* Trimesh + pyglet for the 3D models

## Usage

Install python using your preferred method of installing python. I initially used poetry, but migrating it to another computer turned out to be a real nightmare, so a requirements.txt file is also provided. 

There's some sample scripts provided under the tests/ directory, but you may need to add src/pyDXHR to the path. I'm lazy and I use PyCharm to set the source root.
