meta:
  id: vtxinfo
  endian: le

seq:
  - id: u1
    type: u4
  - id: u2
    type: u4
  - id: len_vtxsem
    type: u2
  - id: len_vtx
    type: u2
  - id: u3
    type: u4
  - id: vtxsem
    type: vtxsem
    repeat: expr
    repeat-expr: 16

types:
  vtxsem:
    seq:
      - id: sem
        type: u4
      - id: offset
        type: u2
      - id: type
        type: u2

