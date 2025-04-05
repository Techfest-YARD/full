import streamlit as st

st.title("📤 Upload PDF Files")

# Upload plików
uploaded_files = st.file_uploader(
    "Wybierz do 10 PDF-ów (max 50MB każdy)",
    type=["pdf"],
    accept_multiple_files=True
)

# Walidacja
if uploaded_files:
    valid_files = [f for f in uploaded_files if f.size < 50 * 1024 * 1024]

    if len(valid_files) > 10:
        st.error("Można przesłać maksymalnie 10 plików.")
    else:
        st.session_state.uploaded_pdfs = valid_files
        st.success(f"Załadowano {len(valid_files)} plików.")

        # Pokaz listę
        for file in valid_files:
            st.write(f"- {file.name} ({round(file.size / 1024 / 1024, 2)} MB)")

        if st.button("➡️ Prześlij i kontynuuj"):
            st.session_state.upload_ready = True
            st.switch_page("pages/1a_Loading.py")