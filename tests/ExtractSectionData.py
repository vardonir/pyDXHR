from pathlib import Path
from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType

# arc = Archive()
# arc.deserialize_from_file(r"F:\DXHR\BIGFILE.000")

# arc = Archive()
# arc.deserialize_from_file(r"F:\DXHRPS3\CACHE.000")

arc = Archive()
arc.deserialize_from_file(r"F:\DXHRDCWII\bigfile-wiiu.000")

# arc = Archive()
# arc.deserialize_from_file(r"C:\Program Files (x86)\GOG Galaxy\Games\Deus Ex HRDC\BIGFILE.000")

# arc = Archive()
# arc.deserialize_from_file(r"F:\DXHRDCPS3\CACHE.000")

# arc = Archive()
# arc.deserialize_from_file(r"F:\DXHRX360Beta\BIGFILE.000")

filename = r"imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_sarif_office\sarif_office_fire_a\sarif_office_fire_a.drm"
# filename = r"shaderlibs\2d1n1s_710c5b2d66d6588e.drm"
data = arc.get_from_filename(filename)
drm = DRM()
drm.deserialize(data)

dest_folder = Path(r"C:\Users\vardo\DXHR_Research\pyDXHR_public\playground\wii_imf") / Path(filename).stem
dest_folder.mkdir(parents=True, exist_ok=True)

# just the section data

for s in drm.Sections:
    if s.Header.SectionType == SectionType.Generic:
        pass
    # elif s.Header.SectionType == SectionType.Material:
    #     with open(dest_folder / f"{s.Header.SectionType.name}_{s.Header.IdHexString}_{s.Header.Specialization}.bin", "wb") as f:
    #         f.write(s.Data)
    else:
        with open(dest_folder / f"{s.Header.SectionType.name}_{s.Header.IdHexString}.bin", "wb") as f:
            f.write(s.Data)

# include header
# for s in drm.SectionData:
#     pass

breakpoint()
