import streamlit as st

st.set_page_config(page_title="TechFest RAG", page_icon="🤖", layout="wide")

st.title("🤖 Witaj w TechFest RAG")
st.markdown("Przejdź do zakładki **Upload** aby dodać pliki PDF, lub do **Chat** żeby rozmawiać.")

if st.button("📤 Przejdź do uploadu"):
    st.switch_page("pages/1_Upload.py")