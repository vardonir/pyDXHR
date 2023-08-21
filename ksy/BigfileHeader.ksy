meta:
  id: bigfile_header

seq:
  - id: alignment
    type: u4le
  - id: bigfile_data
    type: bigfile

types:
  bigfile:
    meta:
      endian:
        switch-on: _root.alignment < 65535
        cases:
          true: be
          _: le
    seq:
      - id: platform
        size: 8
        type: str
        encoding: ascii
      - id: zeroes
        size: 0x38
      - id: len_files
        type: u4
      - id: hash_table
        type: u4
        repeat: expr
        repeat-expr: len_files
      - id: file_headers
        type: file_header
        repeat: expr
        repeat-expr: len_files

    types:
      file_header:
        seq:
          - id: len_uncompressed
            type: u4
          - id: offset
            type: u4
          - id: locale
            type: u4
          - id: len_compressed
            type: u4

