def unpack_from_byte_data(drm_byte_data, drm_name, unpack_destination):
    from pyDXHR.DRM import DRM
    from pyDXHR import SectionType

    drm = DRM.from_bytes(drm_byte_data)
    drm.name = drm_name
    drm.open()

    for sec in drm.sections:
        ext = "bin"

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

        if sec.header.section_type == SectionType.render_resource:
            ext = "pcd"

        write(
            name=drm.name,
            sec_id=sec.header.section_id,
            sec_type=sec.header.section_type.name,
            sec_subtype=sec.header.section_subtype.name,
            extension=ext,
            data=sec.data,
            dest_path=unpack_destination,
        )


def write(name, sec_id, sec_type, sec_subtype, extension, data, dest_path):
    from pathlib import Path

    if isinstance(name, str):
        out_path = Path(dest_path) / name / sec_type / sec_subtype
    elif isinstance(name, int):
        out_path = Path(dest_path) / f"{name:08X}" / sec_type / sec_subtype
    else:
        raise TypeError(f"Invalid type for name: {type(name)}")

    out_path.mkdir(parents=True, exist_ok=True)
    with open(out_path / f"{sec_id:08X}.{extension}", "wb") as f:
        f.write(data)
