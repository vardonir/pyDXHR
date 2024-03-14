from pyDXHR.Bigfile import Bigfile, filelist
from pyDXHR.DRM.Section import FMODSoundBank
from pyDXHR import SectionType
from pyDXHR.DRM import DRM
from pathlib import Path
from tqdm import tqdm

bf = Bigfile.from_env()
bf.open()

fl = filelist.read_filelist("pc-w")
drm_list = [path for _, path in fl.items() if path.endswith(".drm")]

# drm_name = 0xAB0AD4A3
drm_name = r"computer_hacking_a.drm"
# output_dir = Path(r"F:\DXHR_bigfiles\FMOD")

for drm_name in tqdm(drm_list):
    try:
        drm = DRM.from_bigfile(drm_name, bf)
        drm.open()
    except:
        continue

    for idx, sec in enumerate(drm.sections):
        if sec.header.section_type == SectionType.fmod:
            drm_path = Path(drm_name)
            output_dir = Path(r"F:\DXHR_bigfiles\FMOD") / drm_path.stem
            output_dir.mkdir(parents=True, exist_ok=True)

            # if sec.header.section_id == 0x39E:
            #     breakpoint()

            fmod = FMODSoundBank.from_section(sec)
            fmod.read()

            with open(output_dir / f"{idx}.fsb", "wb") as f:
                f.write(fmod.fsb_data)
