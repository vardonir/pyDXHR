from pyDXHR.cdcEngine.Archive import Archive
from pyDXHR.cdcEngine.DRM.UnitDRM import UnitDRM
from pyDXHR.cdcEngine.DRM.DRMFile import DRM

arc = Archive()
arc.deserialize_from_file(r"F:\Games\Deus Ex HRDC\BIGFILE.000")

# one_track_mind = "det_city_sarif.drm"  # the one that matters
# hehe_its_a_track_get_it = "det_city_tunnel1.drm"  # it's a track - useful small unit for testing
# just_a_dipshit_from_detroit = "det_adam_apt_c.drm"  # a lot of everything, but is kinda big
# im_a_fucking_corpo_shill = "det_sarif_industries.drm"  # the one that really matters, but you keep stalling it
file = "det_adam_apt_c.drm"
pc_data = arc.get_from_filename(file)

# pc_drm = UnitDRM()
# pc_drm.deserialize(
#     pc_data,
#     archive=arc,
#     split_by_occlusion=True,
# )

source = r"weapon_combatrifle_world.drm"
dest = r"imf\imf_architecture\imf_interior\imf_detroit\imf_sarif_industries\imf_atrium\det_sarifindustries_bench_a\det_sarifindustries_bench_a.drm"

source_data = arc.get_from_filename(source)
source_drm = DRM()
source_drm.deserialize(source_data)

# TODO: question: if you decompress the DRM and just shove it back to the bigfile, will it still work as expected?

# source_data_repacked = source_drm.serialize()
#
# test = source_data_repacked == source_data[0:len(source_data_repacked)]

breakpoint()

dest_drm = DRM()
dest_drm.deserialize(arc.get_from_filename(dest))

source_model_section = source_drm.Sections[13]
dest_model_section = dest_drm.Sections[16]

arc.Entries = []


from pathlib import Path
new_bigfile = arc.serialize()

for idx, byte_data in enumerate(new_bigfile):
    output_file = fr"F:\Projects\pyDXHR\output\model_swap\test.00{idx}"

    print(f"Writing to {Path(output_file).name}")
    with open(output_file, "wb") as f:
        f.write(byte_data)

print("Final checks")
new_arc = Archive()
new_arc.deserialize_from_file(fr"F:\Projects\pyDXHR\output\model_swap\test.000")

breakpoint()


breakpoint()
