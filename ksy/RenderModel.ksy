meta:
  id: render_model

seq:
  - id: magic
    size: 4
  - id: header
    type: mesh_data

types:
  mesh_data:
    meta:
      endian:
        switch-on: _root.magic
        cases:
          "[0x68, 0x73, 0x65, 0x4D]": be
          "[0x4D, 0x65, 0x73, 0x68]": le
    seq:
      - id: header
        type: mesh_header

    types:
      mesh_header:
        seq:
          - id: flags
            type: u4
          - id: len_data
            type: u4
          - id: len_indices
            type: u4
          - id: bbox_sphere_center
            type: f4
            repeat: expr
            repeat-expr: 4
          - id: bbox_box_min
            type: f4
            repeat: expr
            repeat-expr: 4
          - id: bbox_bbox_max
            type: f4
            repeat: expr
            repeat-expr: 4
          - id: bbox_sphere_radius
            type: f4
          - id: dword44
            type: f4
          - id: dword48
            type: f4
          - id: vs_select4c
            type: u4
          - id: mat_table #?
            type: u4
          - id: ptr_prim_groups
            type: u4
          - id: ptr_mesh_table
            type: u4
          - id: ptr_bones_table
            type: u4
          - id: ptr_indices
            type: u4
          - id: len_mesh_prim
            type: u2
          - id: len_mesh_count
            type: u2
          - id: len_bone_count
            type: u2
          - id: word6a
            type: u2
          - id: dword6c  # end of header
            size: 4
            contents: [0xff, 0xff, 0xff, 0xff]
          - id: dword70
            type: u4
          - id: dword74
            type: u4
          - id: dword78
            type: u4
          - id: dword7c
            type: u4
      mesh_table:
        seq:
          - id: min_dist
            type: f4
          - id: max_dist
            type: f4
          - id: min_fade_dist
            type: f4
          - id: max_fade_dist
            type: f4

          - id: dword10
            type: u4
          - id: dword14
            type: u4
          - id: dword18
            type: u4
          - id: dword1c
            type: u4

          - id: dword20
            type: u4
          - id: dword24
            type: u4
          - id: dword28
            type: u4
          - id: dword2c
            type: u4

          - id: len_mesh_parts
            type: u4
          - id: len_jnt
            type: u4
          - id: offset_mesh_jntmap
            type: u4
          - id: offset_to_vtx_buffer
            type: u4

          - id: static_vertex_buffer #i thought this should be zero?
            type: u4
          - id: dword44
            type: u4
          - id: dword48
            type: u4
          - id: offset_to_vtx_buffer_info
            type: u4

          - id: len_vertices
            type: u4
          - id: start_index_buffer
            type: u4
          - id: num_triangles
            type: u4
          - id: dword5c
            type: u4

        types:
          vtx_sem_info:
            seq:
              - id: u1
                type: u4
              - id: u2
                type: u4
              - id: len_vtx_sem
                type: u2
              - id: len_vtx
                type: u1
              - id: u3
                type: u1
              - id: u4
                type: u4
              - id: semantics
                type: vtx_sem
                repeat: expr
                repeat-expr: len_vtx_sem

          vtx_sem:
            seq:
              - id: sem
                type: u4
              - id: offset
                type: u2
              - id: type
                type: u1
              - id: u1
                type: u1

        instances:
          vtx_sem_info:
            pos: offset_to_vtx_buffer_info
            type: vtx_sem_info


      mesh_prim_header:
        seq:
          - id: vec0
            type: u4
            repeat: expr
            repeat-expr: 4
          - id: start_index
            type: u4
          - id: len_triangles
            type: u4
          - id: dword18
            type: u4
          - id: dword1c
            type: u4
          - id: dword20
            type: u4
          - id: dword24
            type: u4
          - id: ptr_material
            type: u4
          - id: dword2c
            type: u4
          - id: dword30
            type: u4
          - id: dword34
            type: u4
          - id: dword38
            type: u4
          - id: dword3c
            type: u4

    instances:
      mesh_table:
        pos: header.ptr_mesh_table
        type: mesh_table
        repeat: expr
        repeat-expr: header.len_mesh_count
      mesh_prim_table:
        pos: header.ptr_prim_groups
        type: mesh_prim_header
        repeat: expr
        repeat-expr: header.len_mesh_prim
      indices:
        pos: header.ptr_indices
        type: u2
        repeat: expr
        repeat-expr: header.len_indices
