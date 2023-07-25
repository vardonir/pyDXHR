from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.utils import crc32bzip2
from pathlib import Path
from tqdm import tqdm


def populate_filelist_directory(archive: Archive,
                                file_list_path: Path | str,
                                temp_dir: str):
    # get the name hashes in the archive as a set
    arc_hashes = set(e.NameHash for e in archive.Entries)

    files = {}
    with open(file_list_path, "r") as fl:
        for ln in tqdm(fl.readlines(), desc="Populating mock filelist directory, please wait..."):
            complete_path = archive.platform.value + "\\" + ln.strip()
            calc_hash = crc32bzip2(complete_path, dtype=int)
            if calc_hash in arc_hashes:
                files[crc32bzip2(complete_path, dtype=int)] = complete_path
                (temp_dir / Path(complete_path).parent).mkdir(parents=True, exist_ok=True)
                (temp_dir / Path(complete_path)).touch()


def populate_unit_selection_list(
        archive: Archive,
        file_list_path: Path | str,
        temp_dir: str
):

    units = [Path(u).stem for u in archive.unit_list if u.startswith("game")]
    with open(file_list_path, "r") as fl:
        flist = [f.replace(".drm\n", "") for f in fl.readlines()]

        for unit in tqdm(units, desc="Checking valid units, please wait..."):
            if unit in flist:
                (Path(temp_dir) / (unit + ".drm")).touch()


if __name__ == "__main__":
    arc = Archive()
    arc.deserialize_from_env()
    file_list = r"F:\Projects\pyDXHR\external\filelist\generic.txt"

    import tempfile
    with tempfile.TemporaryDirectory() as tf:
        # populate_filelist_directory(arc, file_list, tf)
        populate_unit_selection_list(arc, file_list, tf)

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
