# BIGFILE

Archive file format. 

There are some version differences:

- the PS3 version stores the AV data in `BIGFILE.00*`, the rest in `CACHE.00*`. The same is true for the PS3-DC and PS3-JAP
- the XBox version stores the AV data in `CACHE.00*` with everything else in `BIGFILE.00*`. The same is true for XBox-DC [^1]
- the PC version of the base game stores the game data in `BIGFILE.00*`, and with the localization data stored in `Bigfile_English.000`, `Bigfile_Russian.000`, etc.
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
- 0x00000065 - XBox beta 
- 0x0000D06A - XBox DC [^2]
- 0x0000401F - WiiU

## Filelist?

Each file is stored as a hash instead of a typical filename. You can look up hashing algorithms for what that is and [TheIndra55's cdcResearch page on the Bigfile format](https://cdcengine.re/docs/files/bigfile) on what that means for the game, but basically there's a list of files in there and, looking at the game as it is, there's no way to telling what's the difference between, for example, file 0x4314FB64 or 0x4314FB65. 

That's where the file lists come in. I grabbed these from [Gibbed's tools](https://github.com/gibbed/Gibbed.CrystalDynamics/tree/master/bin_dx3/projects) (although [Erika keeps a more up-to-date one](https://github.com/rrika/dxhr/blob/main/data/Deus%20Ex%203%20-%20Director's%20Cut/files/more.filelist)), and you can end up with a DRM from the game with a human-readable filename, if you run a specific function - in my case, I encode the string to utf-8 and use `bzip2` from the `fastcrc` library, which seems to work out well, but I've seen at least 3 different approaches for it.

pyDXHR uses a "generic" filelist - it's basically the same as the filelists provided in the links, but it strips away the platform-specific prefix, and concatenates all the DXHR filelists into one long list of files. It turns out that you can use a filelist for the PC version on the PS3, for example, if you just replace `pc-w` with `ps3-w`. There's no existing filelist for the Japanese version, but replacing `ps3-w` with `ps3-jap` worked out fine. There are base-specific and DC-specific files (for example, anything relating to TML won't be in base) - pyDXHR skips the files that are not present in the Bigfile archive.

--

[^1]: I'm guessing that XBox-Japan version follows the same format. I'd be happy to check, just send me a copy of the game lmao

[^2]: I'm guessing that the difference is because the game is split to 2 discs, but don't quote me on that