meta:
  id: render_terrain

seq:
  - id: flags
    type: u4le
  - id: data
    type: mesh_data

types:
  mesh_data:
    meta:
      endian:
        switch-on: _root.flags < 65535
        cases:
          true: le
          _: be

    seq:
      - id: header
        type: header

    types:
      header:
        seq:
          - id: offset_node
            type: u4
          - id: len_nodes
            type: u4
          - id: offset_group
            type: u4
          - id: len_group
            type: u4
          - id: offset_vtx_buffer_info
            type: u4
          - id: len_vtx_buffer_info
            type: u2
          - id: unk1
            type: u2
          - id: dword1c
            type: u4
          - id: offset_vb
            type: u4
          - id: len_vb
            type: u2
          - id: unk2
            type: u2
          - id: offset_geom
            type: u4
          - id: len_geom #?
            type: u4
          - id: len_textures
            type: u4
          - id: ptr_indices
            type: u4
          - id: len_indices
            type: u4
          - id: ptr_smth
            type: u4
          - id: len_smth
            type: u4

      something:
        seq:
          - id: idk
            type: u4
            repeat: expr
            repeat-expr: 12

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
      node:
        seq:
          - id: off_list
            type: u4
          - id: nrange
            type: u2

        # instances:
        #   mesh_prim:
        #     pos: off_list
        #     type: mesh_prim_header
        #     repeat: expr
        #     repeat-expr: nrange

        types:
          mesh_prim_header:
            seq:
              - id: start_index
                type: u4
              - id: len_triangles
                type: u4


      group:
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



    instances:
      indices:
        pos: header.ptr_indices
        type: u2
        repeat: expr
        repeat-expr: header.len_indices
      something:
        pos: header.ptr_smth
        type: something
        repeat: expr
        repeat-expr: header.len_smth
      vtx_sem_info:
        pos: header.offset_vtx_buffer_info
        type: vtx_sem_info
        repeat: expr
        repeat-expr: header.len_vtx_buffer_info
      # nodes:
      #   pos: header.offset_geom
      #   type: node
      #   repeat: expr
      #   repeat-expr: header.len_nodes
      groups:
        pos: header.offset_group ## seems related to materials
        type: group
        repeat: expr
        repeat-expr: header.len_group

