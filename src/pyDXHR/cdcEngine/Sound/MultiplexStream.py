import struct
from typing import List
from enum import IntEnum
from pyDXHR.utils import byte_swap
from utils import Endian


class MultiplexStreamHeader:
    _VALID_SAMPLE_RATES = (5512, 11025, 22050, 44100, 48000)

    def __init__(self):
        self._header_data = b""
        self.SampleRate: int = 0
        self.SampleCount: int = 0
        self.ChannelCount: int = 0
        self.FaceDataCount: int = 0
        self.SegmentCount: float = 0
        self.Endian: Endian = Endian.Little

    def deserialize(self, data: bytes):
        self._header_data = data[:0x800]

        sample_rate, = struct.unpack_from("<L", data)
        if sample_rate not in self._VALID_SAMPLE_RATES:
            sample_rate, = struct.unpack_from(">L", data)
            if sample_rate not in self._VALID_SAMPLE_RATES:
                raise Exception
            else:
                self.Endian = Endian.Big
        else:
            self.Endian = Endian.Little

        self.SampleRate = sample_rate

        # data start
        #         public int SampleRate;
        #         public int Unknown004;
        #         public int SampleCount;
        #         public int ChannelCount;
        sample_rate, unk04, self.SampleCount, self.ChannelCount = struct.unpack_from(f"{self.Endian.value}LLLL", data)

        #         [MarshalAs(UnmanagedType.ByValArray, SizeConst = 16)]
        #         public byte[] Unknown010;
        unk10 = struct.unpack_from(f"{self.Endian.value}16B", data, offset=0x10)
        assert not all(unk10)

        #         public uint Unknown020;
        #         public uint Unknown024;
        #         public uint FaceDataSize;
        #         public uint Unknown02C;
        unk20, unk24, self.FaceDataCount, unk2C = struct.unpack_from(f"{self.Endian.value}LLLL", data, offset=0x20)

        #         [MarshalAs(UnmanagedType.ByValArray, SizeConst = 8)]
        #         public byte[] Unknown030;
        unk30 = struct.unpack_from(f"{self.Endian.value}8B", data, offset=0x30)
        assert not all(unk30)

        #         public float SegmentCount;
        #         public float Unknown03C;
        self.SegmentCount, unk3C = struct.unpack_from(f"{self.Endian.value}ff", data, offset=0x38)

        #         [MarshalAs(UnmanagedType.ByValArray, SizeConst = 4)]
        #         public byte[] Unknown040;
        unk40 = struct.unpack_from(f"{self.Endian.value}4B", data, offset=0x40)
        assert not all(unk40)

        #         public float Unknown044;
        unk4, = struct.unpack_from(f"{self.Endian.value}f", data, offset=0x44)

        #         [MarshalAs(UnmanagedType.ByValArray, SizeConst = 36)]
        #         public byte[] Unknown048;
        unk48 = struct.unpack_from(f"{self.Endian.value}36B", data, offset=0x48)
        assert not all(unk48)

        #         public float Unknown06C;
        #         public float Unknown070;
        unk6C, unk70 = struct.unpack_from(f"{self.Endian.value}ff", data, offset=0x6C)

        #         [MarshalAs(UnmanagedType.ByValArray, SizeConst = 4)]
        #         public byte[] Unknown074;
        unk74 = struct.unpack_from(f"{self.Endian.value}4B", data, offset=0x74)
        assert not all(unk74)

        #         public float Unknown078;
        unk78, = struct.unpack_from(f"{self.Endian.value}f", data, offset=0x78)

        #         [MarshalAs(UnmanagedType.ByValArray, SizeConst = 596)]
        #         public byte[] Unknown07C;
        unk7C = struct.unpack_from(f"{self.Endian.value}596B", data, offset=0x7C)
        assert not all(unk7C)

    def swap(self) -> bytes:
        return byte_swap(self._header_data)


class Block:
    def __init__(self):
        self._header_data: bytes = b""
        self.Size: int = 0
        self.Stream: int = 0
        self.Data: bytes = b""

    def __repr__(self):
        return f"Stream {self.Stream} ({self.Size} bytes)"

    def deserialize(self, data, endian: Endian = Endian.Little):
        self._header_data = data[:0x10]
        self.Size, self.Stream, flag, _ = struct.unpack_from(f"{endian.value}LLLL", data)
        assert flag == 0x2001
        self.Data = data[0x10:0x10+self.Size]

    def __eq__(self, other):
        return self.Size == other.Size and self.Stream == other.Stream and self.Data == other.Data

    def swap(self) -> bytes:
        return byte_swap(self._header_data) + self.Data


class SegmentType(IntEnum):
    # ref: https://github.com/gibbed/Gibbed.CrystalDynamics/blob/master/projects/Gibbed.DeusEx3.Demux/Program.cs#L205
    Audio = 0
    Cinematic = 1
    Subtitles = 2
    Unknown = -1


class Segment:
    def __init__(self):
        self._header_data: bytes = b''
        self._segment_data: bytes = b""
        self.SegmentType: SegmentType = SegmentType.Unknown
        self.SegmentSize: int = 0
        self.Blocks: List[Block] = []

    def __repr__(self):
        return f'{self.SegmentType.name} ({self.SegmentSize} bytes)'

    def deserialize(self, data, endian: Endian = Endian.Little):
        self._header_data = data[:0x10]

        seg_type, self.SegmentSize, _, unk8 = struct.unpack_from(f"{endian.value}LLLL", data)
        self.SegmentType = SegmentType(seg_type)
        assert unk8 == 0

        if self.SegmentType in (SegmentType.Cinematic, SegmentType.Subtitles):
            self._segment_data = data[0x10:self.SegmentSize]
            return

        pos = 4 * 4
        while pos < self.SegmentSize:
            bck = Block()
            bck.deserialize(data[pos:], endian=endian)
            self.Blocks.append(bck)

            pos += self.SegmentSize + 0xF
            pos = (pos + 0x0F) & (~0x0F)

    def swap(self) -> bytes:
        out_data = byte_swap(self._header_data)
        out_data += self._segment_data
        for bl in self.Blocks:
            out_data += bl.swap()
            for pad in range((4 - (self.SegmentSize % 4)) % 4):
                out_data += b"\x00"
        return out_data


class MultiplexStream:
    def __init__(self):
        self.Header: MultiplexStreamHeader = MultiplexStreamHeader()
        self.Segments: List[Segment] = []

    def __repr__(self):
        return f"Sample Rate {self.Header.SampleRate} | Channels {self.Header.ChannelCount}"

    def deserialize(self, data: bytes):
        self.Header.deserialize(data)

        pos = 0x800
        while pos < len(data):
            seg = Segment()
            seg.deserialize(data[pos:], endian=self.Header.Endian)

            pos += seg.SegmentSize + 0xF
            self.Segments.append(seg)
            pos = (pos + 0x0F) & (~0x0F)

        assert pos == len(data)

    def swap(self) -> bytes:
        # flip the endianness for the headers but leave the block data alone
        out_data = self.Header.swap()

        for seg in self.Segments:
            out_data += seg.swap()
            for pad in range((4 - (len(out_data) % 4)) % 4):
                out_data += b"\x00"
        return out_data

    @property
    def Streams(self) -> bytes:
        # self.Header.ChannelCount
        out_data = b""
        pos = 0
        for seg in self.Segments:
            for blk in seg.Blocks:
                out_data += blk.Data

        return out_data


if __name__ == "__main__":
    pc_en = r"..\..\..\..\..\Never Asked For This\pc-w\FFFFE081\det1_sq02_dia_adam_006b.mul"
    pc_fr = r"..\..\..\..\..\Never Asked For This\pc-w\FFFFE002\det1_sq02_dia_adam_006b.mul"
    pc_gr = r"..\..\..\..\..\Never Asked For This\pc-w\FFFFE004\det1_sq02_dia_adam_006b.mul"
    pc_ru = ""

    ps3_en = r"..\..\..\..\..\Never Asked For This\ps3-w\FFFFE001\det1_sq02_dia_adam_006b.mul"
    ps3_jap = r"..\..\..\..\..\Never Asked For This\ps3-jap\det1_sq02_dia_adam_006b.mul"

    # with open(ps3_en, "rb") as f:
    #     ps3_en_mul = MultiplexStream()
    #     ps3_en_bytes = f.read()
    #     ps3_en_mul.deserialize(ps3_en_bytes)

    with open(pc_en, "rb") as f:
        pc_en_mul = MultiplexStream()
        pc_en_bytes = f.read()
        pc_en_mul.deserialize(pc_en_bytes)

    with open(pc_fr, "rb") as f:
        pc_fr_mul = MultiplexStream()
        pc_fr_bytes = f.read()
        pc_fr_mul.deserialize(pc_fr_bytes)

    with open(pc_gr, "rb") as f:
        pc_gr_mul = MultiplexStream()
        pc_gr_bytes = f.read()
        pc_gr_mul.deserialize(pc_gr_bytes)

    ps3_swapped = ps3_en_mul.swap()

    ps3_swapped_mul = MultiplexStream()
    ps3_swapped_mul.deserialize(ps3_swapped)

    assert len(ps3_swapped) == len(ps3_en_bytes)
    assert len(ps3_swapped) == len(pc_en_bytes)

    with open(ps3_jap, "rb") as f:
        ps3_jap_mul = MultiplexStream()
        ps3_jap_bytes = f.read()
        ps3_jap_mul.deserialize(ps3_jap_bytes)

    breakpoint()
