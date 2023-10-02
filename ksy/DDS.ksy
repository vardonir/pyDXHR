meta:
  id: dds
  file-extension: dds
  endian: le

seq:
  - id: magic
    size: 4
    contents: [0x44, 0x44, 0x53, 0x20]
  - id: len_header
    size: 4
    contents: [0x7c, 0x00, 0x00, 0x00]
  - id: flags
    type: u4
  - id: height
    type: u4
  - id: width
    type: u4
  - id: pitch
    type: u4
  - id: depth
    type: u4
  - id: len_mipmaps
    type: u4
  - id: zeros_20
    size: 44
  - id: thirty_two
    size: 4
    contents: [0x20, 0x00, 0x00, 0x00]
  - id: pixel_fmt
    type: u4
  - id: four_cc
    type: u4
    enum: texture_format
  - id: pixel_size
    type: u4
  - id: pixel_bitmasks
    type: u4
  - id: dw_caps_1
    type: u4
  - id: dw_caps_2
    type: u4
  - id: dw_caps_3
    type: u4
  - id: dw_caps_4
    type: u4
  - id: zeros_70
    size: 16
  - id: payload
    size-eos: true


enums:
  texture_format:
    0x15: a8r8g8b8
    0x31545844: dxt1
    0x33545844: dxt3
    0x35545844: dxt5

