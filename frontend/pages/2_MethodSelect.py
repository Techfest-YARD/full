import streamlit as st

st.set_page_config(page_title="Wybór metody", layout="wide")
st.title("🧠 Wybierz metodę nauki")

if "uploaded_pdfs" not in st.session_state:
    st.warning("Najpierw prześlij pliki PDF na stronie Upload.")
    st.stop()

st.markdown("Kliknij w kafelek, aby wybrać swój styl nauki:")

# Styl dla kafelków
st.markdown("""
<style>
div.stButton > button {
    background-color: #f7f7f7;
    border: 2px solid #e0e0e0;
    padding: 30px;
    width: 100%;
    height: 250px;
    border-radius: 15px;
    text-align: left;
    font-size: 18px;
    transition: 0.2s all ease-in-out;
}
div.stButton > button:hover {
    border: 2px solid #4B8BBE;
    background-color: #f0f8ff;
    box-shadow: 0 0 12px rgba(75,139,190,0.2);
}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    clicked = st.button("👩‍🏫 Metoda nauczyciela\n\nPodejście klasyczne: tłumaczenie pojęć krok po kroku, definicje i przykłady.", key="teacher_tile")
    if clicked:
        st.session_state.selected_method = "teacher"
        st.switch_page("pages/3_Chat.py")

with col2:
    clicked = st.button("💃 Metoda tancerki\n\nPodejście kreatywne: luźne analogie, emocje, skojarzenia, metafory.", key="dancer_tile")
    if clicked:
        st.session_state.selected_method = "dancer"
        st.switch_page("pages/3_Chat.py")
