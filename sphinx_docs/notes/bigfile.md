# BIGFILE

Archive file format. 

There are some version differences:

- the PS3 version stores the AV data in `BIGFILE.00*`, the rest in `CACHE.00*`. The same is true for the PS3-DC and PS3-JAP
- the XBox version stores the AV data in `CACHE.00*` with everything else in `BIGFILE.00*`. The same is true for XBox-DC [^1]
- the PC version of the base game stores the game data in BIGFILE.00*, and with the localization data stored in `Bigfile_English.000`, `Bigfile_Russian.000`, etc.
- PC-DC stores everything in `BIGFILE.00*`, including localization.

The header has the following format for the PC version
```
meta:
  id: bigfile
  endian: le
  
seq: 
  - id: file_alignment
    type: u4
  - id: archive_type
    size: 16
    type: strz
    encoding: utf-8
  - id: zeroes
    size: 0x30
  - id: len_files
    type: u4
  - id: hash
    type: u4
    repeat: expr
    repeat-expr: len_files
  - id: entries
    type: entry_data
    repeat: expr
    repeat-expr: len_files
    
types:
  entry_data:
    seq:
      - id: len_uncompressed
        type: u4
      - id: off_entry
        type: u4
      - id: spec
        type: u4
      - id: len_compressed
        type: u4      
```
The console version is the same, except that the endian is BE.

Known file alignment values:

- 0x7FF00000 - all PC versions, including TML
- 0x0000F07F - all PS3 versions (base, Japan, DC)
- 0x00003062 - XBox base
- 0x00000065 - XBox Beta 
- 0x0000D06A - XBox DC
- 0x0000401F - WiiU

## Filelist?

TODO 


## See also

- [cdcResearch page on the Bigfile format](https://cdcengine.re/docs/files/bigfile)

--

[^1]: I'm guessing that XBox-Japan version follows the same format. I don't have that version of the game. 
