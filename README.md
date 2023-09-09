# pyDXHR

Python-based data inspection and modification tools for Deus Ex: Human Revolution

## Motivation

All the other tools ([except for one](https://github.com/rrika/dxhr)) that I found for extracting assets for Crystal Engine, the proprietary game engine that DXHR uses, are written in either C# or C++ ([these tools are listed in the references page of pyDXHR's documentation](https://pydxhr.vardonir.com/references.html))... which is fine and dandy if you speak those languages. I don't. And I wanted to get a ton of in-game assets from DXHR [for another project of mine](https://six.vardonir.com/).

Okay, so why not just use those tools and be done with it? What if I only wanted a certain class of models in this export? What if I wanted the models not to have textures attached to them on export? What if I wanted to do some preprocessing on the models that Blender can't handle? I don't speak C++ (yet) or C# (anymore), but I do speak Python. So, I took the codebases from those other Crystal Engine projects, studied them, and lumped them together into this.

## Usage/Documentation

I (will) try to work on it from time to time on [pydxhr.vardonir.com](pydxhr.vardonir.com).

There are currently precompiled binaries available for unpacking Bigfiles, decompressing and generating GLTF models from pre-extracted DRM files. I'm also planning binaries on dumping the textures and material data, generating full GLTF models of the game's maps, and unpacking section data.

## Comments? 

- https://vardonir.com/contact.html
- [my username]@gmail.com
- [my username]@proton.me
- You might also be able to find me on Discord, Reddit, Tumblr, ArtStation, and Twitter. Reddit is preferred.

No guarantees that I'll answer.

## Disclaimer

I am affiliated with Eidos Montreal/Crystal Dynamics, the Embracer Group, or Square Enix. 

I'm just a hypercaffeinated programmer who really needs to learn the meaning of "scope creep."