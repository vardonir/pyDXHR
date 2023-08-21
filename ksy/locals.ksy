meta:
  id: locals
  file-extension: bin
  endian: le

seq:
  - id: unk0
    size: 4
    doc: unknown value
  - id: len_strings
    type: u2
    doc: number of strings in the file
  - id: unk6
    size: 2
    doc: unknown value
  - id: str_list
    type: string
    repeat: expr
    repeat-expr: len_strings

types:
  string:
    seq:
      - id: offset
        type: u4

    instances:
      body:
        pos: offset
        terminator: 0

