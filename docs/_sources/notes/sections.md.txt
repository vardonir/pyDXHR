# DRM sections

Each DRM file contains several sections - some contain texture/mesh data, animation, shader code, etc., basically everything except for audio and video. 

## Section Types

```
    Generic = 0
    Empty = 1
    Animation = 2
    Unknown03 = 3  # PushBuffer?
    Unknown04 = 4  # PushBuffer
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
    Unknown11 = 11
    Sound = 13
    Unknown16 = 16
    Unknown17 = 17
    Unknown18 = 18
    Unknown19 = 19
    Unknown20 = 20
    Unknown21 = 21
    RenderTerrain = 24
    Unknown25 = 25
    RenderModel = 26
    RenderModelBuffer = 27 
    Unknown28 = 28
    Unknown30 = 30
    Unknown32 = 32
    Unknown34 = 34
    Unknown36 = 36
    SmartScript = 40
    Scaleform = 41
    Conversation = 42
    Unknown48 = 48  
    CameraShake = 50
    Unknown52 = 52  
```


## RenderMesh

RenderMesh sections can come in three subtypes: RenderTerrain, RenderModel, and RenderModelBuffer, with the last one specific to the console versions.

The names come from the file lists found in the console version of the game.

### RenderTerrain 

Typically found in streamobjects and unit DRMs. These are typically large meshes, with more than 10 materials at a time. A good example - the entire helipad in the Sarif HQ is one big RenderTerrain, including the background buildings.

### RenderModel and RenderModelBuffer

Usually found in IMFs and objects. 

For the PC version, the RenderModel section data is split between a header, which contains information about bones/joints and material IDs, and the mesh data itself (indices and vertices). On the console versions, the RenderModel section is only the header, and RenderModelBuffer contains the mesh data separately.

Note: `RenderModel.ksy` assumes that it's reading data starting from the `Mesh` data portion of the section.

## RenderResource / Texture

As the name implies.

The PC version uses PCD9 files, the PS3 version uses a very similar format albeit with a different header.

TODO: check the Xbox and Wii-U versions

## CollisionMesh

TODO

## Material

TODO 

hoo boy
