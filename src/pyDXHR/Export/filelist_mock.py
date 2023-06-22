from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.utils import crc32bzip2
from pathlib import Path


def populate_filelist_directory(archive: Archive,
                                file_list_path: Path | str,
                                temp_dir: str):
    # get the name hashes in the archive as a set
    arc_hashes = set(e.NameHash for e in archive.Entries)

    files = {}
    with open(file_list_path, "r") as fl:
        for ln in fl.readlines():
            complete_path = archive.platform.value + "\\" + ln.strip()
            calc_hash = crc32bzip2(complete_path, dtype=int)
            if calc_hash in arc_hashes:
                files[crc32bzip2(complete_path, dtype=int)] = complete_path
                (temp_dir / Path(complete_path).parent).mkdir(parents=True, exist_ok=True)
                (temp_dir / Path(complete_path)).touch()


if __name__ == "__main__":
    arc = Archive()
    arc.deserialize_from_env()
    file_list = r"F:\Projects\pyDXHR\external\filelist_generic.txt"

    import tempfile
    with tempfile.TemporaryDirectory() as tf:
        populate_filelist_directory(arc, file_list, tf)

        filetypes = (
            ('cdcEngine DRM files', '*.drm'),
            ('All files', '*.*')
        )

        from tkinter import filedialog as fd
        filename = fd.askopenfilename(
            filetypes=filetypes,
            initialdir=tf,
        )

        selected = str(Path(filename).relative_to(tf))

        print(selected)
