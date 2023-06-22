from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
from pathlib import Path

arc = Archive()
arc.deserialize_from_env()

scenario_database = r"scenario_database.drm"
# scenario_database = r"scenario_chooser.drm"

sce_drm = DRM()
sce_drm.deserialize(arc.get_from_filename(scenario_database))

breakpoint()
