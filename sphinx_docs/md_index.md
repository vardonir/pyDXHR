# pyDXHR Documentation

Python-based tools for data exploration and extraction of Deus Ex Human Revolution, intended for use in another project of mine: [Project SI-X](https://six.vardonir.com/)

Although I went a bit too far and somehow managed to make a basic mod tool? There's a bigfile repacker in there somewhere.

There was an attempt to make the docs look and feel like a professionally-written document. An attempt. I didn't succeed. This entire thing is basically me talking to myself because I know I'm going to forget what the hecko is going on with the code in about two hours.

The project is not affiliated with Eidos Interactive Corporation, Embracer Group AB, or Square Enix Europe. 

I'm literally just reading code made by people smarter than I am, and piecing them together. 

## Dependencies

* Python 3.10
* Numpy
* fastcrc
* [kaitaistruct](https://kaitai.io/) - The python-generated code is part of the repo, but the raw KSY files are also included.
* scipy - mostly for handling rotations

For the exporters:

* Textures: Pillow
* Models: [pygltflib](https://gitlab.com/dodgyville/pygltflib) 
* Audio: [vgmstream](https://github.com/vgmstream/vgmstream) - used as a CLI tool with subprocess
* Cinematics: [WannaCRI](https://github.com/donmai-me/WannaCRI)

Demos:

* Jupyter/ipynb
* Trimesh + pyglet for the 3D models

## Usage

Install python using your preferred method of installing python. I initially used poetry, but migrating it to another computer turned out to be a real nightmare, so a requirements.txt file is also provided. 

There's some sample scripts provided under the tests/ directory, but you may need to add src/pyDXHR to the path. I'm lazy and I use PyCharm to set the source root. You may need to use sys.path.append, I guess?

There was a distributable/CLI planned, but there's some import crap going on and I didn't want to deal with it.

Why GLTF? UE5 works well with it and I didn't want to deal with Blender's shenanigans with plugin development. Go use [erika's Blender importer](https://github.com/rrika/dxhr) for that one - this project is very heavily based on it. 

The code should work on any platform, but you may need to change the subprocess commands so that vgmstream will work (right now, it's coded for Windows). 
