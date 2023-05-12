import struct
from pyDXHR.cdcEngine.Sections import AbstractSection
from pyDXHR.cdcEngine.Archive import ArchivePlatform
from enum import Enum, IntFlag


class DX11:
    class ChunkTypes(Enum):
        RDEF = b'RDEF'
        ICFE = b'ICFE'
        ISGN = b"ISGN"
        OSGN = b'OSGN'
        OSG5 = b"OSG5"
        SHEX = b'SHEX'
        STAT = b"STAT"

    class ProgramType(IntFlag):
        PixelShader = 0xFFFF
        VertexShader = 0xFFFE

    def __init__(self, data):
        # self.chunks = []
        self.program_type = None
        self.isgn = None
        self.osgn = None
        baadf00d, self.length, unk1, unk2 = struct.unpack_from("4L", data)
        assert baadf00d == 0xbaadf00d

        self.bytecode = data[0x10: self.length - 0x10]
        assert self.bytecode[0:4] == b"DXBC"

        self._parse_bytecode()

    def __len__(self):
        return len(self.bytecode)

    def _parse_bytecode(self):
        # temporary, probably unnecessary
        one, size, len_chunks = struct.unpack_from("3L", self.bytecode, 0x14)
        assert one == 1
        # assert len(self._bytecode) == size # ??

        chunk_offsets = struct.unpack_from(f"{len_chunks}L", self.bytecode, 0x20)

        for off in chunk_offsets:
            chunk_type = self.bytecode[off:off + 4]
            assert chunk_type in {s.value for s in self.ChunkTypes}

            match self.ChunkTypes(chunk_type):
                case self.ChunkTypes.ISGN | self.ChunkTypes.OSGN:
                    magic, chunk_length, element_count, unk = struct.unpack_from("4L", self.bytecode, off)
                    assert magic in {0x4e475349, 0x4e47534f}

                    d_values = []
                    names = []
                    for i in range(element_count):
                        d = struct.unpack_from("6L", self.bytecode, (off + 0x10) + (0x18 * i))
                        names.append(self.bytecode[d[0] + 8 + off:].split(b'\x00')[0].decode("utf-8"))

                        d_values.append(d)

                    if self.ChunkTypes(chunk_type) == self.ChunkTypes.ISGN:
                        self.isgn = names
                    elif self.ChunkTypes(chunk_type) == self.ChunkTypes.OSGN:
                        self.osgn = names

                    # if "TEXCOORD" in names:
                    #     breakpoint()

                case self.ChunkTypes.RDEF:
                    magic, chunk_length, \
                        len_const_buffer, off_const_buffer, \
                        len_resource_binding, off_resource_binding, \
                        minor_version, major_version, \
                        program_type, flags, \
                        off_to_creator = struct.unpack_from("LLLLLLBBHLL", self.bytecode, off)

                    assert magic == 0x46454452
                    if major_version != 5:
                        breakpoint()

                    if program_type in {0xffff, 0xfffe}:
                        self.program_type = self.ProgramType(program_type)
                    else:
                        pass

                case _:
                    pass

        # breakpoint()

    @property
    def disasm(self):
        # https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/shader-model-5-assembly--directx-hlsl-

        d3d1x_path = r"C:\Users\vardo\DXHR_Research\pyDXHR_public\external\d3d1x_rel_v090b\Release\fxdis.exe"
        import tempfile
        import subprocess
        import os

        fd, path = tempfile.mkstemp(
            dir=r"C:\Users\vardo\DXHR_Research\pyDXHR_public\external\d3d1x_rel_v090b\Release",
            suffix=".bin")
        try:
            with os.fdopen(fd, 'wb') as tf:
                tf.write(self.bytecode)

            result = subprocess.run([d3d1x_path, path],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

        finally:
            os.remove(path)

        return result.stdout.decode("utf-8")

# out = {}
# for dep in drm.Header.DRMDependencies:
#     t_drm = DRM()
#     t_drm.deserialize(arc.get_from_filename(dep))
#
#     for sec in t_drm.Sections:
#         if sec.Header.SectionType == SectionType.ShaderLib:
#             out[hex(sec.Header.SecId)] = sec
#
# a = ShaderLib(section=out.get("0x1d40")).bytecode_chunks[0]
# aa = a.d3d1x_run()


class DX9:
    def __init__(self, data):
        self.length, unk1, unk2, unk3, unk4 = struct.unpack_from("5L", data)

        self.bytecode = data[0x14:self.length + 0x14]
        assert self.bytecode[0:4] == b'CTAB'


class ShaderLib(AbstractSection):
    def __init__(self, **kwargs):
        self.bytecode_chunks = []
        self.sl_type = -1
        self.header_length = -1
        self.headers = []

        super().__init__(**kwargs)

    def _deserialize_from_section(self, sec):
        super()._deserialize_from_section(sec)
        self.spec = sec.Header.Specialization

        cursor = 0
        if self.spec == 0x7FFFFFFF:
            self.sl_type, h2, h3, h4 = struct.unpack_from("4L", sec.Data)
            self.header_length = h2 >> 4

            if self.sl_type == 1 or self.sl_type == 0:
                for i in range(self.header_length):
                    self.headers.append(struct.unpack_from("4L", sec.Data, 0x10 + (0x10*i)))
                cursor = 0x10 + h2

        # else:
        elif self.spec == 0xBFFFFFFF:
            self.sl_type, h2, h3 = struct.unpack_from("LLL", sec.Data)
            self.header_length = h2 >> 4

            if (self.sl_type == 1) or (self.sl_type == 0) or (self.sl_type == 3):
                for i in range(self.header_length):
                    hh1, hh2, hh3, hh4 = struct.unpack_from("4L", sec.Data, 0xC + (0x10*i))
                    self.headers.append((hh1, hh2, hh3, hh4))

                    if self.sl_type != 3:
                        assert hh4 == 0xFFFFFFFF

                cursor = 0xC + (0x10 * self.header_length)

            elif self.sl_type == 2:
                assert self.header_length == 0
                hh1, hh2 = struct.unpack_from("2L", sec.Data, 0xC)
                self.headers.append((hh1, hh2))

                cursor = 0xc + 0x8
        else:
            # this comes up once, in 2d1n1s_710c5b2d66d6588e_dx9
            print(f"Unknown type {sec.Header.Specialization} : {self.sl_type}")
            return

        while cursor < len(self.section.Data):
            cd = self._parse_chunks(sec.Data[cursor:])
            self.bytecode_chunks.append(cd)
            cursor += cd.length

    def _parse_chunks(self, data):
        match self.spec:
            case 0x7FFFFFFF:
                chunk = DX9(data)
            case 0xBFFFFFFF:
                chunk = DX11(data)
            case _:
                raise Exception

        return chunk

    @property
    def info(self):
        return self.sl_type, self.header_length, len(self.bytecode_chunks)

    @staticmethod
    def _get_name_from_archive(archive, sec_id):
        if archive is not None and archive.platform.value in ArchivePlatform.has_complete_file_lists():
            return archive.section_list[sec_id]
        else:
            return "ShaderLib_" + f"{sec_id:x}".rjust(8, '0')

    def to_gltf(self):
        raise Exception("???")


def from_drm(drm):
    sl = [ShaderLib(section=sec) for sec in drm.Sections]
    # sl_types = [i.spec for i in sl]
    sl_type = list({i.spec for i in sl})

    if len(sl_type) != 1:
        return None
    else:
        if sl_type[0] == 0x7FFFFFFF:
            assert len(sl) == 13
        else:
            assert len(sl) == 19 or len(sl) == 9

        return sl
