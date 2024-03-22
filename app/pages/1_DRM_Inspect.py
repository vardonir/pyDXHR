import streamlit as st
from pyDXHR.DRM import DRM
from pyDXHR import SectionType, SectionSubtype
from pyDXHR.DRM.Section import RenderResource


st.title("DXHR DRM Inspector")

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()

    if bytes_data[0:4] != b'CDRM':
        st.write("is not valid CDRM file")

    else:
        drm = DRM.from_bytes(bytes_data)
        drm.open()

        st.download_button(
            label="Decompress",
            data=drm.decompressed_bytes,
            file_name=uploaded_file.name + ".decompressed.drm",
            key="decompress"
        )

        if len(drm.drm_deps) > 0:
            with st.expander("DRM dependencies"):
                for d in drm.drm_deps:
                    st.write(d)

        if len(drm.obj_deps) > 0:
            with st.expander("Object dependencies"):
                for o in drm.obj_deps:
                    st.write(o)

        with st.expander("DRM section summary: "):
            st.write(f"Root section index: {'None' if drm.root_section_index == 0xFFFFFFFF else drm.root_section_index}")
            st.table(drm.section_summary())

        st.header("Sections:")
        for idx, sec in enumerate(drm.sections):
            st.write(
                f"{idx}: ",
                sec.header.section_type.name,
                sec.header.section_subtype.name,
                f"({sec.header.specialization:08X})",
                f"{sec.header.len_data} bytes"
            )

            st.download_button(
                label="Download",
                data=sec.data,
                file_name=f"{sec.header.section_id:08X}.bin",
                key=f"{sec.header.section_id:08X}_{sec.header.specialization:08X}"
            )

            if sec.header.section_type == SectionType.render_resource:
                rr = RenderResource.from_section(sec)
                if rr is not None:
                    image = rr.read()
                    dds = image.to_dds(None)

                    st.download_button(
                        label="Download DDS",
                        data=dds,
                        file_name=f"{sec.header.section_id:08X}.dds",
                        key=f"{sec.header.section_id:08X}.dds"
                    )


# todo:
#  - download fmod sections as fsb4
#  - download rendermesh sections as gltf
#  - download scaleform sections as cfx
#  - convert MUL to FSB
#  - demux USM
