from pathlib import Path
from tqdm import tqdm
from pyDXHR.cdcEngine.Archive import Archive, ArchivePlatform
from pyDXHR.cdcEngine.DRM.DRMFile import DRM
from pyDXHR.cdcEngine.DRM.SectionTypes import SectionType
from pyDXHR.cdcEngine.DRM.Sections.RenderResource import RenderResource, OutputFormat


def generate(
        archive: Archive,
        destination: str | Path,
        use_named_paths: bool = False,
        output_format: OutputFormat = OutputFormat.TGA
):
    processed_textures = []

    for entry in tqdm(archive.Entries, desc="Processing archive entries"):
        entry_data = archive.get_entry_data(entry)
        drm = DRM()
        stat = drm.deserialize(entry_data)

        if stat:
            tex_sec_list = drm.filter_by_type([SectionType.RenderResource])
            for tex in tex_sec_list:
                if tex.Header.SecId in processed_textures:
                    continue
                else:
                    rr = RenderResource(section=tex)
                    if use_named_paths:
                        dest_path = Path(destination) / Path(archive.texture_list[tex.Header.SecId]).parent
                        dest_path.mkdir(parents=True, exist_ok=True)
                        rr.to_file(output_format,
                                   save_to=dest_path / (Path(archive.texture_list[tex.Header.SecId]).stem.replace("|", "_") + f".{output_format.value}"))
                    else:
                        rr.to_file(output_format,
                                   save_to=Path(destination) / f"{tex.Header.IdHexString}.{output_format.value}")
                    processed_textures.append(tex.Header.SecId)

    print(f"Found {len(processed_textures)} textures")
