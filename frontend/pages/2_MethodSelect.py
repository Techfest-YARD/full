import streamlit as st

st.set_page_config(page_title="Wybór metody", layout="wide")
st.title("🧠 Wybierz metodę nauki")

if "uploaded_pdfs" not in st.session_state:
    st.warning("Najpierw prześlij pliki PDF na stronie Upload.")
    st.stop()

st.markdown("Kliknij w kafelek, aby wybrać swój styl nauki:")

# CSS styling for grid tiles with fixed size and black text
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
    color: black;
    transition: 0.2s all ease-in-out;
}
div.stButton > button:hover {
    border: 2px solid #4B8BBE;
    background-color: #f0f8ff;
    box-shadow: 0 0 12px rgba(75,139,190,0.2);
}
</style>
""", unsafe_allow_html=True)

# Arrange 6 methods in a grid (2 rows x 3 columns)
row1_cols = st.columns(3)
row2_cols = st.columns(3)

# Row 1
with row1_cols[0]:
    if st.button("💬 Chat z notatkami\n\nInteraktywna rozmowa oparta na notatkach.", key="chat_notes_tile"):
        st.session_state.selected_method = "chat_with_notes"
        st.switch_page("pages/2_ChatWithNotes.py")
with row1_cols[1]:
    if st.button("📇 Metoda Fiszek\n\nZapamiętuj informacje za pomocą fiszek.", key="flashcards_tile"):
        st.session_state.selected_method = "flashcards"
        st.switch_page("pages/4_Flashcards.py")
with row1_cols[2]:
    if st.button("📅 Metoda Planu\n\nPlanowanie nauki w czasie.", key="study_plan_tile"):
        st.session_state.selected_method = "study_plan"
        st.switch_page("pages/5_StudyPlan.py")

# Row 2
with row2_cols[0]:
    if st.button("🧐 Metoda Ciekawego dziecka\n\nZachęca do zadawania pytań i głębszej refleksji.", key="curious_child_tile"):
        st.session_state.selected_method = "curious_child"
        st.switch_page("pages/6_CuriousChild.py")
with row2_cols[1]:
    if st.button("👩‍🏫 Metoda Nauczyciela\n\nUcz poprzez tłumaczenie materiału innym.", key="teacher_tile"):
        st.session_state.selected_method = "teacher"
        st.switch_page("pages/7_Teacher.py")
with row2_cols[2]:
    if st.button("📝 Metoda Testów\n\nSprawdź swoją wiedzę przez testy.", key="tests_tile"):
        st.session_state.selected_method = "tests"
        st.switch_page("pages/8_Tests.py")
