import streamlit as st


notes = st.file_uploader("Choose a notes file",type=["pdf","docx"])

exam = st.file_uploader("Choose a exam file",type=["json"])

if st.button("Take the exam"):

    st.success("**Exam Solved**")