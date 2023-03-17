from cdcEngine.Archive import Archive, ArchivePlatform


def _decode_text(raw_data: bytes, encoding: str = "ascii"):
    decoded = raw_data.decode(encoding)
    decoded_list = decoded.split("\r")
    return {int(it.split(",")[0].strip()): it.split(",")[1] for it in decoded_list if len(it.split(",")) > 1}


def object_list(archive: Archive):
    obj_list_raw = archive.get_from_filename("objectlist.txt")
    if obj_list_raw is None:
        return {}

    return _decode_text(obj_list_raw)


def unit_list(archive: Archive):
    unit_list_raw = archive.get_from_filename("unitlist.txt")
    if unit_list_raw is None:
        return []

    unit_list_decoded = [it.decode("ascii") for it in unit_list_raw.split()]
    _ = int(unit_list_decoded.pop(0))
    return unit_list_decoded


def texture_list(archive: Archive):
    match archive.platform.value:
        case ArchivePlatform.PS3_W.value:
            raw_list = archive.get_from_hash(2979602415)  # 0xB1991FEF
        case ArchivePlatform.PS3_JAP.value:
            raise NotImplementedError
        case _:
            return {}

    if raw_list is None:
        return {}

    return _decode_text(raw_list, encoding="latin1")


def section_list(archive: Archive):
    match archive.platform.value:
        case ArchivePlatform.PS3_W.value:
            raw_list = archive.get_from_hash(4128657984)  # 0xF6165240
        case ArchivePlatform.PS3_JAP.value:
            raw_list = archive.get_from_hash(4162441112)  # F819CF98
        case _:
            return {}

    if raw_list is None:
        return {}

    return _decode_text(raw_list, encoding="latin1")


def animation_list(archive: Archive):
    match archive.platform.value:
        case ArchivePlatform.PS3_W.value:
            raw_list = archive.get_from_hash(2974621525)  # 0xB14D1F55
        case ArchivePlatform.PS3_JAP.value:
            raise NotImplementedError
        case _:
            return {}

    if raw_list is None:
        return {}

    return _decode_text(raw_list, encoding="latin1")


def sound_effects_list(archive: Archive):
    match archive.platform.value:
        case ArchivePlatform.PS3_W.value:
            raw_list = archive.get_from_hash(1117682290)  # 0x429E7A72
        case ArchivePlatform.PS3_JAP.value:
            raise NotImplementedError
        case _:
            return {}

    if raw_list is None:
        return {}

    return _decode_text(raw_list, encoding="latin1")


def something_list(archive: Archive):
    # there's something here, but I have no idea what it is...
    return {}
#     match archive.platform.value:
#         case ArchivePlatform.PS3_W.value:
#             raw_list = archive.get_from_hash(43068992)  # 0x02912E40
#         case ArchivePlatform.PS3_JAP.value:
#             raise NotImplementedError
#         case _:
#             return {}
#
#     return _decode_text(raw_list, encoding="latin1")
