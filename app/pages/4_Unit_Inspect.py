import streamlit as st
from pyDXHR.DRM.unit import UnitDRM


st.header("Unit inspector")

uploaded_file = st.file_uploader("Choose a file")
read_objectlist = st.checkbox("Read objectlist.txt (DC only)")

object_dict = {}
if read_objectlist:
    with open("pages/objectlist.txt", "r") as f:
        obj_list = f.read().split("\n")

        for i, obj in enumerate(obj_list):
            if i == 0:
                continue
            if i == len(obj_list) - 1:
                continue

            obj_id, obj_name = obj.split(",")
            obj_id = int(obj_id.strip())
            obj_name = obj_name.strip()
            object_dict[obj_id] = obj_name

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()

    if bytes_data[0:4] != b'CDRM':
        st.write("is not valid CDRM file")

    else:
        drm = UnitDRM.from_bytes(bytes_data)
        drm.read_objects()
        drm.read_imfs()

        if len(drm.int_imf_map):
            with st.expander("INT IMF"):
                for key, locs in drm.int_imf_map.items():
                    st.write(f"{key:08X}: {len(locs)}")

        if len(drm.ext_imf_map):
            with st.expander("EXT IMF"):
                for key, locs in drm.ext_imf_map.items():
                    st.write(f"{key}: {len(locs)}")

        if len(drm.obj_map):
            with st.expander("Objects"):
                for key, obj in drm.obj_map.items():
                    if len(object_dict):
                        st.write(f"{object_dict[key]}: {len(obj)}")
                    else:
                        st.write(f"{key:08X}: {len(obj)}")

        if len(drm.cell_map):
            with st.expander("Cells"):
                for key, locs in drm.cell_map.items():
                    st.write(f"{key:08X}: {len(locs)}")

        if len(drm.streamgroup_map):
            with st.expander("Stream"):
                for (path, name), locs in drm.streamgroup_map.items():
                    st.write(name)

        if len(drm.occlusion_map):
            with st.expander("Occlusion"):
                for key, locs in drm.occlusion_map.items():
                    st.write(f"{key:08X}: {len(locs)}")
