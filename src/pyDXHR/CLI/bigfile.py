from pathlib import Path
import sys

def check_bigfile(file_path: str | Path) -> bool:
    from cdcEngine.Archive import Archive
    bigfile = list(Path(file_path).glob("bigfile.000"))
    if len(bigfile):
        print(f"Found {bigfile[0]}")
        try:
            arc = Archive()
            arc.deserialize_from_file(bigfile[0])
        except:
            print("Cannot open BIGFILE. Closing program")
            sys.exit(0)
        else:
            print(arc)
            return True
