import streamlit as st
import time

# Set page configuration – must be called first.
st.set_page_config(page_title="Przetwarzanie...", layout="centered")

st.title("⏳ Przetwarzanie plików...")
st.markdown("Twoje pliki są przesyłane do backendu. To może chwilę potrwać.")

# Upewnij się, że pliki PDF zostały wcześniej przesłane.
if "uploaded_pdfs" not in st.session_state or not st.session_state.get("upload_ready", False):
    st.warning("Najpierw prześlij pliki na stronie Upload.")
    st.stop()

# Jeśli backend_response jeszcze nie istnieje – symuluj przetwarzanie.
if "backend_response" not in st.session_state:
    with st.spinner("Wysyłanie plików do backendu..."):
        time.sleep(2)  # Symulacja czasu przetwarzania
        # Zapisz przykładową odpowiedź w stanie sesji.
        st.session_state.backend_response = {"status": "ok", "message": "Pliki przetworzone"}
        st.success("✅ Pliki przetworzone!")
        # Wymuś ponowne uruchomienie skryptu, aby UI zaktualizowało stan.
        try:
            st.experimental_rerun()
        except AttributeError:
            st.stop()
else:
    # Jeśli już przetworzono, przełącz na stronę wyboru metody.
    st.switch_page("2_MethodSelect")
