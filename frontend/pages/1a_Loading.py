import streamlit as st
from connectors.ApiBackend import ApiBackend

st.set_page_config(page_title="Przetwarzanie...", layout="centered")

st.title("⏳ Przetwarzanie plików...")
st.markdown("Twoje pliki są przesyłane do backendu. To może chwilę potrwać.")

if "uploaded_pdfs" not in st.session_state or not st.session_state.upload_ready:
    st.warning("Najpierw prześlij pliki na stronie Upload.")
    st.stop()

# Tylko raz
if "backend_response" not in st.session_state:

    with st.spinner("Wysyłanie plików do backendu..."):
        try:
            backend = ApiBackend()
            result = backend.upload_files(st.session_state.uploaded_pdfs)

            st.session_state.backend_response = result
            st.success("✅ Pliki przetworzone!")
            st.switch_page("pages/2_MethodSelect.py")

        except Exception as e:
            st.error(f"❌ Błąd podczas przesyłania plików: {e}")
            st.stop()

else:
    # Jeśli już było przetwarzane, przejdź dalej
    st.switch_page("pages/2_MethodSelect.py")