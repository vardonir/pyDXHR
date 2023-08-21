Valid values for 


; version: "base", "dc", "beta", "tml", "japan"
pydxhr_use_version="base"

; platform: "pc", "ps3", "360", "wiiu"
pydxhr_use_platform="pc"



run makespec: 
pyi-makespec --onefile .\pyDXHR\entrypoints\drm_decompress.py

if filelist is needed in exe, include
    datas= [ ('pyDXHR/Bigfile/filelist/generic.txt', 'pyDXHR/Bigfile/filelist' ) ],


drm to gltf, bigfile unpack, drm decompress, drm unpack, and bigfile pack executables are intended to run on their own, no .env file needed

unit to gltf requires an env file
