meta:
  id: dxhr_drm
  file-extension: drm
doc: |
  Parser for decompressed DRM files used in Crystal Engine games. Tested on
  DRMs from Deus Ex Human Revolution, PC and PS3. Adapted from
  Gibbed.CrystalDynamics code, TheIndra55's cdcResearch notes,
  rrika's cdcEngineDXHR, and many others.

seq:
  - id: version
    type: u4le
    doc: |
      DRM version. For DXHR, this is 0x15
  - id: drm_data
    type: drm

types:
  drm:
    meta:
      endian:
        switch-on: _root.version < 65535
        cases:
          true: le
          _: be
    seq:
      - id: len_drm_dependencies
        type: u4
      - id: len_obj_dependencies
        type: u4
      - id: unk0c
        type: u4
      - id: unk10
        type: u4
      - id: flags
        type: u4
      - id: len_sections
        type: u4
      - id: root_section
        type: u4
      - id: section_headers
        type: section_header(_index)
        repeat: expr
        repeat-expr: len_sections
      - id: obj_dependencies
        size: len_obj_dependencies
        type: str
        encoding: ascii
        doc: |
          OBJ dependencies - needs to be split by null
      - id: drm_dependencies
        size: len_drm_dependencies
        type: str
        encoding: ascii
        doc: |
          DRM dependencies  - needs to be split by null. These are paths and
          should end in .drm
      - id: sections
        type: section(_index, _io.pos)
        repeat: expr
        repeat-expr: len_sections

    types:
      section:
        doc: |
          Section (relocs + payload) data.

        params:
          - id: idx
            type: u4
          - id: start_offs
            type: u4

        seq:
          - id: align
            size: (16 - (_io.pos % 16)) % 16
            if: _parent.flags & 1 == 1

          - id: relocs
            size: _parent.section_headers[idx].len_relocs

          - id: align2
            size: (16 - (_io.pos % 16)) % 16
            if: _parent.flags & 1 == 1

          - id: payload
            size: _parent.section_headers[idx].len_data

      section_header:
        params:
          - id: idx
            type: u4

        seq:
          - id: len_data
            type: u4
          - id: type
            type: u1
            enum: section_type
          - id: unk05
            type: u1
          - id: unk06
            type: u2
          - id: flags
            type: u4
          - id: sec_id
            type: u4
          - id: spec
            type: u4
            doc: |
              Specialization mask - others call this "Language". Mostly used
              to differentiate between the material sections for the PC version,
              but it has other uses, I guess.

        instances:
          len_relocs:
            value: (flags & 0xFFFFFF00) >> 8
          section_subtype:
            value: ((flags >> 1) & 0x7f)
            enum: section_subtype

enums:
  section_type:
    0: generic
    1: empty
    2: animation
    5: render_resource
    6: fmod
    7: dtpdata
    8: script
    9: shaderlib
    10: material
    11: object
    12: render_mesh
    13: collision_mesh
    14: stream_group_list
    -1: unknown

  section_subtype:
    0: generic
    5: texture
    11: unknown_11
    13: sound
    16: fsfx
    17: lights
    18: unknown_18
    20: unknown_20
    21: unknown_21
    24: render_terrain
    25: unknown_25
    26: render_model
    27: render_model_buffer
    28: unknown_28
    30: unknown_30
    32: unknown_32
    34: fxfxa
    36: unknown_36
    40: smart_script
    41: scaleform
    42: conversation
    50: camera_shake
    -1: unknown
