doc: |
  Texture image type used in the PS3 version of the game. 

meta:
  id: ps3t
  endian: be

enums:
  texture_format:
    133: a8r8g8b8
    124: dxt1
    165: dxt3
    136: dxt5

seq:
  - id: magic
    contents: "PS3T"
  - id: len_data
    type: u4
  - id: unk_8
    type: u2
  - id: unk_a
    type: u2
  - id: format
    type: u1
    enum: texture_format
  - id: unk_d
    type: u1
  - id: unk_e
    type: u2
  - id: unk_10
    type: u4
  - id: height
    type: u2
  - id: width
    type: u2
  - id: unk_18
    type: u4
  - id: unk_1c
    type: u4
  - id: unk_20
    type: u4
  - id: payload
    size: len_data
