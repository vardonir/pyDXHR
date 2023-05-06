from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.Export.ArchiveUnpack import unpack_archive

arc = Archive()
arc.deserialize_from_file(r"C:\Users\vardo\DXHR_Research\DXHRDCWII\bigfile-wiiu.000")

unpacked_destination_path = r"C:\Users\vardo\DXHR_Research\DXHRDCWII"
file_list = r"C:\Users\vardo\DXHR_Research\pyDXHR_public\external\filelist_generic.txt"
unpack_archive(archive=arc, dest_path=unpacked_destination_path, file_list=file_list)
