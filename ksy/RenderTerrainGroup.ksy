meta:
  id: renderterrain_group
  endian: le

seq:
  - id: idx_material
    type: u4
  - id: idx_vb
    type: u4
  - id: flags
    type: u2
  - id: unk
    type: u2
  - id: render_passes
    type: u4
  - id: instance_texture_indices
    type: u4
    repeat: expr
    repeat-expr: 4
