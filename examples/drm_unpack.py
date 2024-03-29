from pyDXHR.Bigfile import Bigfile
from pyDXHR.DRM import DRM
from pyDXHR import SectionType

# Assumes that you have the PC Director's Cut edition specified in env
bf = Bigfile.from_env(version=Bigfile.Version.DIRECTORS_CUT, platform=Bigfile.Platform.PC)
# bf.unpack_from = "cache"
bf.open()

# drm = DRM.from_bigfile(0xAB0AD4A3, bf)
drm = DRM.from_bigfile("email_database.drm", bf)
drm.open()

out = r"C:\Users\vardo\Documents\pyDXHR\playground"
convert_textures = True


def write(name, sec_id, sec_type, sec_subtype, extension, data):
    from pathlib import Path
    if isinstance(name, str):
        out_path = Path(out) / name / sec_type / sec_subtype
    elif isinstance(name, int):
        out_path = Path(out) / f"{name:08X}" / sec_type / sec_subtype
    else:
        raise TypeError(f"Invalid type for name: {type(name)}")

    out_path.mkdir(parents=True, exist_ok=True)
    with open(out_path / f"{sec_id:08X}.{extension}", "wb") as f:
        f.write(data)


for sec in drm.sections:

    if sec.header.section_type == SectionType.material:
        if sec.header.specialization == 0xBFFFFFFF:
            ext = "mtl_a"
        elif sec.header.specialization == 0x7FFFFFFF:
            ext = "mtl_b"
        else:
            ext = "mtl"
    if sec.header.section_type == SectionType.shaderlib:
        if sec.header.specialization == 0xBFFFFFFF:
            ext = "shdr_a"
        elif sec.header.specialization == 0x7FFFFFFF:
            ext = "shdr_b"
        else:
            ext = "shdr"

    else:
        ext = "bin"

    write(drm.name, sec.header.section_id, sec.header.section_type.name, sec.header.section_subtype.name, ext, sec.data)
