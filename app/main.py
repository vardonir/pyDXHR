import streamlit as st

st.title("DXHR Tools")

st.write("Collection of tools for working with Deus Ex: Human Revolution's game files, powered by pyDXHR")

st.header("Web tools")

st.write("These tools assume that you have already unpacked the game's bigfile.")

st.page_link("pages/1_DRM_Inspect.py", label="DRM inspect")

st.page_link("pages/2_MUL_Converter.py", label="MUL to FSB4 converter: TODO")

st.page_link("pages/3_Bigfile_Repack.py", label="Bigfile repacker: TODO")

st.page_link("pages/4_Unit_Inspect.py", label="Unit inspect")

st.header("CLI tools")

st.markdown("[Bigfile unpacker]()")

st.markdown("[GLTF converter]()")
