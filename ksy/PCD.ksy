doc: |
  Texture image type used in the PC version of the game. 

meta:
  id: pcd
  endian: le

enums:
  texture_format:
    0x15: a8r8g8b8
    0x31545844: dxt1
    0x33545844: dxt3
    0x35545844: dxt5

seq:
  - id: magic
    contents: "PCD9"
  - id: format
    type: u4
    enum: texture_format
  - id: len_data
    type: u4
  - id: len_mipmaps
    type: u4
  - id: width
    type: u2
  - id: height
    type: u2
  - id: unk14
    type: u4
  - id: unk18
    type: u4
  - id: payload
    size: len_data
