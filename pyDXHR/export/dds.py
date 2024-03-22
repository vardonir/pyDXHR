from pathlib import Path
from enum import Enum
from typing import Optional


class TextureFormat(Enum):
    """
    This is intended to "translate" the textureformats specified in the generated KSY enums
    """

    A8R8G8B8 = "a8r8g8b8"
    DXT1 = "dxt1"
    DXT3 = "dxt3"
    DXT5 = "dxt5"


class Image:
    def __init__(self, height, width, tex_fmt_str, payload=b"", len_mipmaps=0, name=""):
        self.Name = name
        self.Height = height
        self.Width = width
        self.LenMipMaps = len_mipmaps
        self.Format = TextureFormat(tex_fmt_str)
        self.Payload = payload
        self._dds_blob: bytes = b""

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
            case TextureFormat.A8R8G8B8.value:
                return int(4 * self.Height * self.Width)
            case TextureFormat.DXT1.value:
                blk_size = 8
            case TextureFormat.DXT3.value | TextureFormat.DXT5.value:
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
            case TextureFormat.A8R8G8B8.value:
                return flags_rgb | flags_alpha_pixels
            case TextureFormat.DXT1.value | TextureFormat.DXT3.value | TextureFormat.DXT5.value:
                return flags_fourcc
            case _:
                raise Exception("Format not found")

    def _fourcc(self):
        match self.Format.value:
            case TextureFormat.A8R8G8B8.value:
                return 0
            case TextureFormat.DXT1.value:
                return 827611204
            case TextureFormat.DXT3.value:
                return 861165636
            case TextureFormat.DXT5.value:
                return 894720068
            case _:
                raise Exception("Format not found")

    def _dwCaps1(self):
        flags_complex = 0x8
        flags_mipmap = 0x400000
        flags_texture = 0x1000

        out = flags_texture
        if self.LenMipMaps > 0:
            out |= flags_complex | flags_mipmap
        return out

    def _dwCaps2(self):
        pass

    def _pixel_size(self):
        match self.Format.value:
            case TextureFormat.A8R8G8B8.value:
                return 32
            case TextureFormat.DXT1.value | TextureFormat.DXT3.value | TextureFormat.DXT5.value:
                return 0
            case _:
                raise Exception("Format not found")

    def _pixel_bitmasks(self):
        match self.Format.value:
            case TextureFormat.A8R8G8B8.value:
                return 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000
            case TextureFormat.DXT1.value | TextureFormat.DXT3.value | TextureFormat.DXT5.value:
                return 0, 0, 0, 0
            case _:
                raise Exception("Format not found")

    def build_dds_blob(self):
        import struct

        dds_magic = b"\x44\x44\x53\x20"
        len_dds_header = 124

        self._dds_blob += dds_magic

        # TODO: FIX ME
        # region DDS header
        self._dds_blob += struct.pack(
            "<7I44x",
            int(len_dds_header),
            self._flags(),
            self.Height,
            self.Width,
            self._pitch(),
            0,  # self.depth,
            self.LenMipMaps,
        )

        self._dds_blob += struct.pack(
            "<8I",
            32,
            self._pixel_format(),
            self._fourcc(),
            self._pixel_size(),
            *self._pixel_bitmasks(),
        )

        self._dds_blob += struct.pack(
            "<4I4x",
            self._dwCaps1(),  # dwCaps1
            0,  # dwCaps2 - no cubemaps in DXHR
            0,  # dwCaps3 = 0
            0,  # dwCaps4 = 0
        )
        # endregion

        assert len(self._dds_blob) == len_dds_header + 4

        self._dds_blob += self.Payload
        return self._dds_blob

    def to_dds(self, save_to: Optional[str | Path] = None) -> Optional[bytes]:
        """Return the DDS blob as bytes or save to path"""
        if len(self._dds_blob) == 0:
            self.build_dds_blob()

        if save_to:
            with open(Path(save_to) / (self.Name + ".dds"), "wb") as f:
                f.write(self._dds_blob)
        else:
            return self._dds_blob

    def _blob_to_fmt(self, img_fmt):
        from PIL import Image as PILImage
        from io import BytesIO

        dds_image = PILImage.open(BytesIO(self._dds_blob))
        out_im_buffer = BytesIO()
        dds_image.save(out_im_buffer, format=img_fmt)
        return out_im_buffer.getvalue()

    def to_png(self, save_to: Optional[str | Path] = None) -> Optional[bytes]:
        if len(self._dds_blob) == 0:
            self.build_dds_blob()

        png_blob = self._blob_to_fmt("png")
        if save_to:
            with open(Path(save_to) / (self.Name + ".png"), "wb") as f:
                f.write(png_blob)
        else:
            return png_blob

    def to_tga(self, save_to: Optional[str | Path] = None) -> Optional[bytes]:
        if len(self._dds_blob) == 0:
            self.build_dds_blob()

        tga_blob = self._blob_to_fmt("tga")
        if save_to:
            with open(Path(save_to) / (self.Name + ".tga"), "wb") as f:
                f.write(tga_blob)
        else:
            return tga_blob

    def to_raw(self, save_to: Optional[str | Path] = None) -> Optional[bytes]:
        if save_to:
            with open(Path(save_to) / (self.Name + ".raw"), "wb") as f:
                f.write(self.Payload)
        else:
            return self.Payload
