import streamlit as st
from openai import OpenAI
from connectors.ApiBackend import ApiBackend

st.set_page_config(page_title="Chatbot", layout="wide")
st.title("💬 Chatbot")

# Zainicjalizuj ApiBackend
backend = ApiBackend()

# Inicjalizacja historii czatu
if "messages" not in st.session_state:
    st.session_state.messages = []

# Wyświetlenie wcześniejszych wiadomości
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Pole do wpisania promptu
if prompt := st.chat_input("Zadaj pytanie do swoich notatek:"):

    # Dodaj wiadomość użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Odpowiedź z backendu
    with st.chat_message("assistant"):
        with st.spinner("Myślę..."):
            try:
                response = backend.ask_chat(prompt)
                st.markdown(response)
            except Exception as e:
                response = f"❌ Błąd: {e}"
                st.error(response)

    # Dodaj odpowiedź asystenta
    st.session_state.messages.append({"role": "assistant", "content": response})
