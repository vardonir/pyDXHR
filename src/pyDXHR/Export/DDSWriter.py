"""
Flags values adapted from
https://github.com/drewcassidy/quicktex/blob/main/quicktex/dds.py
https://www.xnalara.org/viewtopic.php?t=1001
"""

import struct
from enum import Enum
from io import BytesIO
from PIL import Image
from pathlib import Path
from typing import Any


class TextureFormat(Enum):
    a8r8g8b8 = 21, 133
    dxt1 = 827611204, 134
    dxt3 = 861165636, 165
    dxt5 = 894720068, 136

    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj._true_value = values[0]
        for other_value in values[1:]:
            cls._value2member_map_[other_value] = obj
        obj._all_values = values
        return obj

    def __repr__(self):
        return '<%s.%s: %s>' % (
                self.__class__.__name__,
                self._name_,
                ', '.join([repr(v) for v in self._all_values]),
                )

    @property
    def value(self) -> Any:
        return self._true_value


class OutputFormat(Enum):
    DDS = "dds"
    PNG = "png"
    TGA = "tga"


class DDSImage:
    _magic = b'\x44\x44\x53\x20'
    _len_header = 124

    def __init__(self,
                 height: int,
                 width: int,
                 texture_format: int,
                 len_mipmaps: int = 0,
                 payload: bytes = b""):
        self.Height = height
        self.Width = width
        self.Format = TextureFormat(texture_format)
        self.Payload = payload
        self.LenMipMaps = len_mipmaps
        self._dds_blob: bytes = b""

        self._build_blob()

    def _flags(self):
        caps = 0x1
        height = 0x2
        width = 0x4
        # PITCH = 0x8
        pixel_format = 0x1000
        mipmap_count = 0x20000
        linear_size = 0x80000
        # DEPTH = 0x800000

        out = caps | height | width | pixel_format | linear_size
        if self.LenMipMaps > 0:
            out |= mipmap_count

        return out

    def _pitch(self):
        rows = max([1, int((self.Height + 3) / 4)])
        cols = max([1, int((self.Width + 3) / 4)])

        match self.Format.value:
            case TextureFormat.a8r8g8b8.value:
                return int(4 * self.Height * self.Width)
            case TextureFormat.dxt1.value:
                blk_size = 8
            case TextureFormat.dxt3.value | TextureFormat.dxt5.value:
                blk_size = 16
            case _:
                raise Exception("Format not found")
        return int(rows * cols * blk_size)

    def _pixel_format(self):
        flags_alpha_pixels = 0x1
        # ALPHA = 0x2
        flags_fourcc = 0x4
        flags_rgb = 0x40
        # YUV = 0x200
        # LUMINANCE = 0x20000

        match self.Format.value:
            case TextureFormat.a8r8g8b8.value:
                return flags_rgb | flags_alpha_pixels
            case TextureFormat.dxt1.value | TextureFormat.dxt3.value | TextureFormat.dxt5.value:
                return flags_fourcc
            case _:
                raise Exception("Format not found")

    def _fourcc(self):
        match self.Format.value:
            case TextureFormat.a8r8g8b8.value:
                return 0
            case TextureFormat.dxt1.value | TextureFormat.dxt3.value | TextureFormat.dxt5.value:
                return self.Format.value
            case _:
                raise Exception("Format not found")

    def _dwCaps1(self):
        flags_complex = 0x8
        flags_mipmap = 0x400000
        flags_texture = 0x1000

        out = flags_texture
        if self.LenMipMaps > 0:
            out |= (flags_complex | flags_mipmap)
        return out

    def _dwCaps2(self):
        pass

    def _pixel_size(self):
        match self.Format.value:
            case TextureFormat.a8r8g8b8.value:
                return 32
            case TextureFormat.dxt1.value | TextureFormat.dxt3.value | TextureFormat.dxt5.value:
                return 0
            case _:
                raise Exception("Format not found")

    def _pixel_bitmasks(self):
        match self.Format.value:
            case TextureFormat.a8r8g8b8.value:
                return 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000
            case TextureFormat.dxt1.value | TextureFormat.dxt3.value | TextureFormat.dxt5.value:
                return 0, 0, 0, 0
            case _:
                raise Exception("Format not found")

    def _build_blob(self):
        self._dds_blob += self._magic

        # TODO: FIX ME
        # region DDS header
        self._dds_blob += struct.pack(
            '<7I44x',
            int(self._len_header),
            self._flags(),
            self.Height,
            self.Width,
            self._pitch(),
            0,  # self.depth,
            self.LenMipMaps,
        )

        self._dds_blob += struct.pack(
            '<8I',
            32,
            self._pixel_format(),
            self._fourcc(),
            self._pixel_size(),
            *self._pixel_bitmasks()
            )

        self._dds_blob += struct.pack(
            '<4I4x',
            self._dwCaps1(),  # dwCaps1
            0,  # dwCaps2 - no cubemaps in DXHR
            0,  # dwCaps3 = 0
            0  # dwCaps4 = 0
        )
        # endregion

        assert len(self._dds_blob) == self._len_header + 4

        self._dds_blob += self.Payload

    def write_as(self, image_format: OutputFormat = OutputFormat.DDS):
        match image_format:
            case OutputFormat.DDS:
                return self._dds_blob
            case OutputFormat.PNG | OutputFormat.TGA:
                dds_image = Image.open(BytesIO(self._dds_blob))
                out_im_buffer = BytesIO()
                dds_image.save(out_im_buffer, format=image_format.value)
                return out_im_buffer.getvalue()
            case _:
                raise NotImplementedError

    def save_as(self, image_format: OutputFormat, save_to: Path | str):
        with open(save_to, "wb") as f:
            f.write(self.write_as(image_format))
