from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
from pyDXHR.cdcEngine.Sections import RenderMesh
from pathlib import Path

arc = Archive()
arc.deserialize_from_env()

output_path = r"F:\Projects\pyDXHR\output\scenario_models"

scenario_list_from_unitlist = [i.split("\\")[-1] + ".drm" for i in arc.unit_list if i.startswith("scenario")]
file_list = r"..\external\filelist_generic.txt"
file_list = Path(file_list).read_text().split("\n")

scenario = [i for i in file_list if i in scenario_list_from_unitlist]

for sce in scenario:
    sce_drm = DRM()
    sce_drm.deserialize(arc.get_from_filename(sce))

    for idx, sec in enumerate(sce_drm.Header.SectionHeaders):
        if sec.SectionType == SectionType.RenderMesh:
            rm_sec = sce_drm.Sections[idx]
            rm = RenderMesh.deserialize(rm_sec)
            rm.to_gltf(save_to=fr"{output_path}\{sce}")

