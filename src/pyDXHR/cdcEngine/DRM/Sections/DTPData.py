# https://github.com/rrika/cdcEngineDXHR/blob/main/cdcResource/DTPDataSection.h

from pyDXHR.cdcEngine.DRM.Sections import AbstractSection
from pyDXHR.cdcEngine.Archive import ArchivePlatform


class DTPData(AbstractSection):
    # TODO

    @staticmethod
    def _get_name_from_archive(archive, sec_id):
        if archive is not None and archive.platform.value in ArchivePlatform.has_complete_file_lists():
            return archive.section_list[sec_id]
        else:
            return "DTP_" + f"{sec_id:x}".rjust(8, '0')

    def to_gltf(self):
        raise NotImplementedError

    def _deserialize_from_section(self, sec):
        super()._deserialize_from_section(sec)
