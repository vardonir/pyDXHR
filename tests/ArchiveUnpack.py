from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.Export.ArchiveUnpack import unpack_archive

arc = Archive()
# arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHR 1.0.499.0 beta\BIGFILE.000")
# arc.deserialize_from_file(r"F:\Projects\pyDXHR\bigfiles\DXHRX360Beta\cache.000")
arc.deserialize_from_env("PS3_DC")

unpacked_destination_path = r"F:\Projects\pyDXHR\bigfiles\DXHRDCPS3\PYDXHR"
file_list = r"..\external\filelist_generic.txt"
unpack_archive(
    archive=arc,
    dest_path=unpacked_destination_path,
    file_list=file_list,
    only_unknown=True,
    decompress_drm=True
)
