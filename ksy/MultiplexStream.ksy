meta:
  id: multiplex_stream
  endian: le

seq:
  - id: header
    type: header
  - id: padding
    size: 0x734
  - id: segments
    type: segment
    repeat: eos

types:
  header:
    seq:
      - id: sample_rate
        type: u4
      - id: loop_start
        type: u4
      - id: loop_end
        type: u4
      - id: len_channel
        type: u4
      - id: reverb_volume
        type: u4
      - id: start_size_to_load
        type: u4
      - id: partial_loop
        type: u4
      - id: len_loop_area
        type: u4
      - id: has_cinematic
        type: u4
      - id: has_subtitles
        type: u4
      - id: len_face_fx
        type: u4
      - id: offs_loop_start_file
        type: u4
      - id: offs_loop_start_bundle
        type: u4
      - id: max_ee_bytes_per_read
        type: u4
      - id: len_media
        type: f4
      - id: volume_left
        type: f4
        repeat: expr
        repeat-expr: 12
      - id: volume_right
        type: f4
        repeat: expr
        repeat-expr: 12
      - id: loop_start_samples_to_skip
        type: u4
        repeat: expr
        repeat-expr: 12

  segment:
    seq:
      - id: segment_header
        type: segment_header
      - id: data
        size: segment_header.len_segment
        if: segment_header.type != segment_type::audio
      - id: blocks
        type: block
        if: segment_header.type == segment_type::audio
      - id: padding
        size: (16 - (_io.pos % 16)) % 16


  segment_header:
    seq:
      - id: type
        type: u4
        enum: segment_type
      - id: len_segment
        type: u4
      - id: unk08
        type: u4
      - id: zero
        type: u4

  block:
    seq:
      - id: header
        type: block_header
      - id: data
        size: header.size

  block_header:
    seq:
      - id: size
        type: u4
      - id: stream
        type: u4
      - id: flag
        type: u4
      - id: unk0c
        type: u4

enums:
  segment_type:
    0: audio
    1: cinematic
    2: subtitle
