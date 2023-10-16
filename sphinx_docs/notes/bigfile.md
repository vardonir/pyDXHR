# BIGFILE

Archive file format. 

There are some version differences:

- the PS3 version stores the AV data in `BIGFILE.00*`, the rest in `CACHE.00*`. The same is true for the PS3-DC and PS3-JAP
- the XBox version seems to have the data mixed in the `CACHE.00*` and `BIGFILE.00*`.
- the Wii-U version stores the data in smaller `bigfile-wiiu.00*` files, along with `dlcpack-wiiu.00*` files.
- the PC version of the base game stores the game data in `BIGFILE.00*`, and with the localization data stored in `Bigfile_English.000`, `Bigfile_Russian.000`, etc. There are `patch*.000` files for the base game, as well, which I presumably for updates.
- PC Director's Cut stores everything in `BIGFILE.00*`, including localization data.

(Only on this page, "localization" refers to the non-English audio and texts. The same term is used elsewhere in this documentation to refer to something else.)

The kaitai struct file for the header is as follows:
```
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
```
Only the header is read using the KSY file.

Known file alignment values:

- 0x7FF00000 - all PC versions, including TML
- 0x0000F07F - all PS3 versions (base, Japan, DC) + Xbox cache
- 0x00003062 - XBox base bigfile
- 0x00000065 - XBox beta bigfile
- 0x0000D06A - XBox DC bigfile, disc 1
- 0x0000006B - XBox DC bigfile, disc 2
- 0x0000401F - WiiU


## Filelist?

Each file is stored as a hash instead of a typical filename. You can look up hashing algorithms for what that is and [TheIndra55's cdcResearch page on the Bigfile format](https://cdcengine.re/docs/files/bigfile) on what that means for the game, but basically there's a list of files in there and, looking at the game as it is, there's no way to telling what's the difference between, for example, file 0x4314FB64 or 0x4314FB65. 

That's where the file lists come in. I grabbed these from [Gibbed's tools](https://github.com/gibbed/Gibbed.CrystalDynamics/tree/master/bin_dx3/projects) (although [Erika keeps a more up-to-date one](https://github.com/rrika/dxhr/blob/main/data/Deus%20Ex%203%20-%20Director's%20Cut/files/more.filelist)), and you can end up with a DRM from the game with a human-readable filename, if you run a specific function - in my case, I encode the string to utf-8 and use `bzip2` from the `fastcrc` library, which seems to work out well, but I've seen at least 3 different approaches for it.

pyDXHR uses a "generic" filelist - it's basically the same as the filelists provided in the links above, but it strips away the platform-specific prefix, and concatenates all the known DXHR filelists into one long list of files. This is because you can use a filelist for the PC version on PS3 files, for example, if you just replace `pc-w` with `ps3-w`. There's no existing filelist for the Japanese version, but replacing `ps3-w` with `ps3-jap` worked out fine. There are base-specific and DC-specific files (for example, anything relating to TML won't be in base), and console-specific files (`shaderlib/*_dx11.drm` would mean nothing in the console versions) - pyDXHR skips the files that are not present in the Bigfile archive.

## `pc-dev`

One thing that the generic filelist skips are the `pc-dev` files:
```
pc-dev\animlist.ids
pc-dev\boneid.ids
pc-dev\dtpdata.ids
pc-dev\objectlist.ids
pc-dev\textures.ids
pc-dev\waves.ids
```

These are found only in the PC DC version, providing a list of the sections and their human-readable filenames (although the lists are too short to correspond to the entire game. I'm guessing these were for TML and were left over).

There are `xenon-w\*.ids` and `ps3-w\*.ids` files, however, except for the Xenon-DC version, and they seem to be complete.
