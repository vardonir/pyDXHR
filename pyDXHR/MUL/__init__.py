from pathlib import Path
from kaitaistruct import KaitaiStructError
from pyDXHR.generated.multiplex_stream import MultiplexStream
from pyDXHR.Bigfile import Bigfile
from typing import Optional


class InvalidMULError(Exception):
    pass


class KaitaiMultiplexStream(MultiplexStream):
    pass


class MUL:
    def __init__(self) -> None:
        self.name: Optional[str | int] = None
        self.data: bytes = b""

        self._kt_mul: Optional[KaitaiMultiplexStream] = None

    def to_fsb(self, path: Optional[str | Path] = None):
        fsb_bytes = b""

        for segment in self._kt_mul.segments:
            if segment.segment_header.type == MultiplexStream.SegmentType.audio:
                fsb_bytes += segment.blocks[0].data

        if path is not None:
            with open(path, "wb") as f:
                f.write(fsb_bytes)

    def open(self):
        try:
            self._kt_mul = KaitaiMultiplexStream.from_bytes(self.data)
        except KaitaiStructError:
            raise Exception("Failed to parse MUL file")

        # if self._kt_mul.header.sample_rate not in (5512, 11025, 22050, 44100, 48000):
        #     raise InvalidMULError("Invalid sample rate")

    @classmethod
    def from_bytes(
            cls,
            data: bytes,
            name: str | int = None):

        obj = cls()
        obj.name = name
        obj.data = data
        return obj

    @classmethod
    def from_bigfile(
            cls,
            drm_name_or_hash: str | int,
            bigfile: Bigfile,
            locale: int = 0xF
    ):
        try:
            data = bigfile.read(drm_name_or_hash, locale=locale)
        except KeyError:
            data = bigfile.read(drm_name_or_hash + ".mul", locale=locale)

        obj = cls.from_bytes(data)
        if isinstance(drm_name_or_hash, int):
            obj.name = f"{drm_name_or_hash:08X}"
        else:
            obj.name = drm_name_or_hash
        return obj

    @classmethod
    def from_file(cls, file_path: str | Path):
        with open(file_path, "rb") as f:
            data = f.read()
        return cls.from_bytes(data, file_path)

# import struct
# from typing import List
# from enum import IntEnum
# from pyDXHR.utils import byte_swap
# from pyDXHR.cdcEngine.Archive import ArchiveEntry
# from pyDXHR.utils import Endian
#
#
# class MultiplexStreamHeader:
#     # TODO revise me! see https://github.com/rrika/cdcEngineDXHR/blob/main/cdcSound/MultiplexStream.h#L8
#     _VALID_SAMPLE_RATES = (5512, 11025, 22050, 44100, 48000)
#
#     def __init__(self):
#         self._header_data = b""
#         self.SampleRate: int = 0
#         self.SampleCount: int = 0
#         self.ChannelCount: int = 0
#         self.FaceDataCount: int = 0
#         self.SegmentCount: float = 0
#         self.Endian: Endian = Endian.Little
#
#     def deserialize(self, data: bytes):
#         self._header_data = data[:0x800]
#
#         sample_rate, = struct.unpack_from("<L", data)
#         if sample_rate not in self._VALID_SAMPLE_RATES:
#             sample_rate, = struct.unpack_from(">L", data)
#             if sample_rate not in self._VALID_SAMPLE_RATES:
#                 raise Exception
#             else:
#                 self.Endian = Endian.Big
#         else:
#             self.Endian = Endian.Little
#
#         self.SampleRate = sample_rate
#
#         # data start
#         #         public int SampleRate;
#         #         public int Unknown004;
#         #         public int SampleCount;
#         #         public int ChannelCount;
#         sample_rate, unk04, self.SampleCount, self.ChannelCount = struct.unpack_from(f"{self.Endian.value}LLLL", data)
#
#         #         [MarshalAs(UnmanagedType.ByValArray, SizeConst = 16)]
#         #         public byte[] Unknown010;
#         unk10 = struct.unpack_from(f"{self.Endian.value}16B", data, offset=0x10)
#         assert not all(unk10)
#
#         #         public uint Unknown020;
#         #         public uint Unknown024;
#         #         public uint FaceDataSize;
#         #         public uint Unknown02C;
#         unk20, unk24, self.FaceDataCount, unk2C = struct.unpack_from(f"{self.Endian.value}LLLL", data, offset=0x20)
#
#         #         [MarshalAs(UnmanagedType.ByValArray, SizeConst = 8)]
#         #         public byte[] Unknown030;
#         unk30 = struct.unpack_from(f"{self.Endian.value}8B", data, offset=0x30)
#         assert not all(unk30)
#
#         #         public float SegmentCount;
#         #         public float Unknown03C;
#         self.SegmentCount, unk3C = struct.unpack_from(f"{self.Endian.value}ff", data, offset=0x38)
#
#         #         [MarshalAs(UnmanagedType.ByValArray, SizeConst = 4)]
#         #         public byte[] Unknown040;
#         unk40 = struct.unpack_from(f"{self.Endian.value}4B", data, offset=0x40)
#         assert not all(unk40)
#
#         #         public float Unknown044;
#         unk4, = struct.unpack_from(f"{self.Endian.value}f", data, offset=0x44)
#
#         #         [MarshalAs(UnmanagedType.ByValArray, SizeConst = 36)]
#         #         public byte[] Unknown048;
#         unk48 = struct.unpack_from(f"{self.Endian.value}36B", data, offset=0x48)
#         assert not all(unk48)
#
#         #         public float Unknown06C;
#         #         public float Unknown070;
#         unk6C, unk70 = struct.unpack_from(f"{self.Endian.value}ff", data, offset=0x6C)
#
#         #         [MarshalAs(UnmanagedType.ByValArray, SizeConst = 4)]
#         #         public byte[] Unknown074;
#         unk74 = struct.unpack_from(f"{self.Endian.value}4B", data, offset=0x74)
#         assert not all(unk74)
#
#         #         public float Unknown078;
#         unk78, = struct.unpack_from(f"{self.Endian.value}f", data, offset=0x78)
#
#         #         [MarshalAs(UnmanagedType.ByValArray, SizeConst = 596)]
#         #         public byte[] Unknown07C;
#         unk7C = struct.unpack_from(f"{self.Endian.value}596B", data, offset=0x7C)
#         assert not all(unk7C)
#
#     def swap(self) -> bytes:
#         return byte_swap(self._header_data)
#
#     def to_bytes(self):
#         return self._header_data
#
#
# class Block:
#     def __init__(self):
#         self._header_data: bytes = b""
#         self.Size: int = 0
#         self.Stream: int = 0
#         self.Data: bytes = b""
#
#     def __repr__(self):
#         return f"Stream {self.Stream} ({self.Size} bytes)"
#
#     def deserialize(self, data, endian: Endian = Endian.Little):
#         self._header_data = data[:0x10]
#         self.Size, self.Stream, flag, _ = struct.unpack_from(f"{endian.value}LLLL", data)
#         assert flag == 0x2001
#         self.Data = data[0x10:0x10+self.Size]
#
#     def __eq__(self, other):
#         return self.Size == other.Size and self.Stream == other.Stream and self.Data == other.Data
#
#     def swap(self) -> bytes:
#         return byte_swap(self._header_data) + self.Data
#
#     def to_bytes(self):
#         return self._header_data + self.Data
#
#
# class SegmentType(IntEnum):
#     # ref: https://github.com/gibbed/Gibbed.CrystalDynamics/blob/master/projects/Gibbed.DeusEx3.Demux/Program.cs#L205
#     Audio = 0
#     Cinematic = 1
#     Subtitles = 2
#     Unknown = -1
#
#
# class Segment:
#     def __init__(self):
#         self._header_data: bytes = b''
#         self._segment_data: bytes = b""
#         self.SegmentType: SegmentType = SegmentType.Unknown
#         self.SegmentSize: int = 0
#         self.Blocks: List[Block] = []
#
#     def __repr__(self):
#         return f'{self.SegmentType.name} ({self.SegmentSize} bytes)'
#
#     def deserialize(self, data, endian: Endian = Endian.Little):
#         self._header_data = data[:0x10]
#
#         seg_type, self.SegmentSize, _, unk8 = struct.unpack_from(f"{endian.value}LLLL", data)
#         self.SegmentType = SegmentType(seg_type)
#         assert unk8 == 0
#
#         if self.SegmentType in (SegmentType.Cinematic, SegmentType.Subtitles):
#             self._header_data = data[:0x10 + 8]
#             self._segment_data = data[(0x10+8):0x10+self.SegmentSize]
#             return
#
#         pos = 4 * 4
#         while pos < self.SegmentSize:
#             bck = Block()
#             bck.deserialize(data[pos:], endian=endian)
#             self.Blocks.append(bck)
#
#             pos += self.SegmentSize + 0xF
#             pos = (pos + 0x0F) & (~0x0F)
#
#     def swap(self) -> bytes:
#         out_data = byte_swap(self._header_data)
#         out_data += self._segment_data
#         for bl in self.Blocks:
#             out_data += bl.swap()
#         return out_data
#
#     def to_bytes(self):
#         out_data = self._header_data
#         out_data += self._segment_data
#         for bl in self.Blocks:
#             out_data += bl.to_bytes()
#         return out_data
#
#
# class MultiplexStream:
#     def __init__(self):
#         self.Header: MultiplexStreamHeader = MultiplexStreamHeader()
#         self.Segments: List[Segment] = []
#
#     def __repr__(self):
#         return f"""
#         Sample Rate {self.Header.SampleRate}
#         Sample Count  {self.Header.SampleCount}
#         Channel Count  {self.Header.ChannelCount}
#         Face Data Count  {self.Header.FaceDataCount}
#         Segment Count {self.Header.SegmentCount}
#         """
#
#     def deserialize(self, data: bytes):
#         self.Header.deserialize(data)
#
#         pos = 0x800
#         while pos < len(data):
#             seg = Segment()
#             seg.deserialize(data[pos:], endian=self.Header.Endian)
#
#             pos += seg.SegmentSize + 0xF
#             self.Segments.append(seg)
#             pos = (pos + 1 + 0x0F) & (~0x0F)
#
#         assert pos == len(data)
#
#     def swap(self) -> bytes:
#         # flip the endianness for the headers but leave the block data alone
#         out_data = self.Header.swap()
#
#         for seg in self.Segments:
#             out_data += seg.swap()
#
#             len_diff = ((16 - len(out_data)) % 16) % 16
#             out_data += b"\x00"*len_diff
#         return out_data
#
#     def to_bytes(self):
#         out_data = self.Header.to_bytes()
#
#         for seg in self.Segments:
#             out_data += seg.to_bytes()
#
#             len_diff = ((16 - len(out_data)) % 16) % 16
#             out_data += b"\x00"*len_diff
#         return out_data
#
#     @property
#     def Streams(self) -> bytes:
#         # self.Header.ChannelCount
#         out_data = b""
#         for seg in self.Segments:
#             for blk in seg.Blocks:
#                 out_data += blk.Data
#
#         return out_data
#
#     def to_archive_entry(self,
#                          name_hash: int = 0,
#                          locale: int = 0xffffffff,
#                          offset: int = 0,
#                          swap: bool = False
#                          ) -> ArchiveEntry:
#         entry = ArchiveEntry()
#         entry.CompressedSize = 0  # I believe MUL files are not compressed at all...
#         entry.UncompressedSize = len(self.to_bytes())
#         entry.Locale = locale
#         entry.NameHash = name_hash
#         entry.Offset = offset
#
#         if swap:
#             entry.EntryData = self.swap()
#         else:
#             entry.EntryData = self.to_bytes()
#         return entry
#
#
# if __name__ == "__main__":
#     from pyDXHR.cdcEngine.Archive import Archive
#
#     never_asked_for_this = r"audio\streams\vo\eng\det1\adam_jensen\sq02\det1_sq02_dia_adam_006b.mul"
#     problematic = r"audio\streams\vo\eng\det_sam\npcs\unique\det_david_sarif\cp01\sam_cp01_dia_sari_037_alt.mul"
#
#     pc_dc = r"F:\Games\Deus Ex HRDC\BIGFILE.000"
#     ps3_bigfile = ""
#
#     pc_arc = Archive()
#     pc_arc.deserialize_from_file(pc_dc)
#
#     pc_en_data = pc_arc.get_from_filename(never_asked_for_this, spec=0xffffe081)
#
#     pc_en = MultiplexStream()
#     pc_en.deserialize(pc_en_data)
#
#     ps3_jap = r"C:\Users\vardo\DXHR_Research\JAP\BIGFILE.000"
#
#     ps3_arc = Archive()
#     ps3_arc.deserialize_from_file(ps3_jap)
#
#     ps3_en_data = ps3_arc.get_from_filename(never_asked_for_this, spec=0xffffe001)
#     ps3_ja_data = ps3_arc.get_from_filename(never_asked_for_this, spec=0xffffe020)
#
#     ps3_en = MultiplexStream()
#     ps3_en.deserialize(ps3_en_data)
#
#     ps3_en_swapped_data = ps3_en.swap()
#     ps3_en_swapped = MultiplexStream()
#     ps3_en_swapped.deserialize(ps3_en_swapped_data)
#
#     assert ps3_en_swapped.to_bytes() == pc_en_data
#
#     ps3_ja = MultiplexStream()
#     ps3_ja.deserialize(ps3_ja_data)
#     ps3_ja_swapped_data = ps3_ja.swap()
#
#     breakpoint()
