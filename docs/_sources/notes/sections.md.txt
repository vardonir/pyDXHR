# DRM sections

Each DRM file contains several sections - some contain texture/mesh data, animation, shader code, etc., basically everything except for audio and video. 

## Section Types

```
    Generic = 0
    Empty = 1
    Animation = 2
    Unknown03 = 3  
    Unknown04 = 4  
    RenderResource = 5
    FMODSoundBank = 6  # or Wave
    DTPData = 7
    Script = 8
    ShaderLib = 9
    Material = 10
    Object = 11
    RenderMesh = 12
    CollisionMesh = 13
    StreamGroupList = 14
    AnyType = 15
```

And each section sometimes comes with a section-specific subtype:

```
    Generic = 0 
    Texture = 5
    Sound = 13
    RenderTerrain = 24
    RenderModel = 26
    RenderModelBuffer = 27 
    SmartScript = 40
    Scaleform = 41
    Conversation = 42
    CameraShake = 50
```

There are subsections with unknown names (such as Unknown 18 showing up with material sections) - these are listed in the KSY files so that the parser won't throw errors, but not listed above.

## RenderMesh

RenderMesh sections can come in three subtypes: RenderTerrain, RenderModel, and RenderModelBuffer, with the last one specific to the console versions.

The names come from the file lists found in the console version of the game.

### RenderTerrain 

Typically found in stream objects and unit DRMs. These are typically large meshes, with more than 10 materials at a time. A good example - the entire helipad in the Sarif HQ is one big RenderTerrain, including the background buildings. A good chunk of Adam's apartment is also a RT.

### RenderModel and RenderModelBuffer

Usually found in IMFs and objects - IMF DRMs contain a single RenderModel, while object DRMs can contain multiple RenderModels. 

For the PC version, the RenderModel section data is split between a header, which contains information about bones/joints and material IDs, and the mesh data itself (indices and vertices). On the console versions, the RenderModel section is only the header, and RenderModelBuffer contains the mesh data separately.

Note: `RenderModel.ksy` assumes that it's reading data starting from the `Mesh` data portion of the section.

## RenderResource / Texture

As the name implies.

The PC version uses PCD9 files, the PS3 version uses a very similar format with a different header.

TODO: check the Xbox and Wii-U versions

## CollisionMesh

TODO

## Material

No.
