import streamlit as st
import os
import requests
from authlib.integrations.requests_client import OAuth2Session

# Must be the very first Streamlit command!
st.set_page_config(page_title="TechFest RAG", page_icon="🤖", layout="wide")

# --- OAuth Configuration ---
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "https://frontend-46193761155.europe-west3.run.app/oauth2callback"  
AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"

# --- Session State Initialization ---
if "user" not in st.session_state:
    st.session_state.user = None
if "oauth_state" not in st.session_state:
    st.session_state.oauth_state = None

# --- Automatic Code Retrieval from URL ---
query_params = st.query_params  # st.query_params is now a property, not callable
if "code" in query_params and st.session_state.user is None:
    code = query_params["code"][0]
    oauth = OAuth2Session(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=["openid", "email", "profile"]
    )
    token = oauth.fetch_token(TOKEN_ENDPOINT, code=code)
    response = oauth.get(USERINFO_ENDPOINT)
    user_info = response.json()
    st.session_state.user = user_info
    # Clear query parameters so the code isn't re-processed on refresh.
    st.set_query_params()

# --- Top-Right Permanent Login/Logout Panel ---
st.markdown("""
    <style>
    .top-right {
        position: fixed;
        top: 10px;
        right: 10px;
        background-color: #f7f7f7;
        padding: 10px;
        border: 1px solid #ccc;
        z-index: 1000;
        border-radius: 5px;
        width: 250px;
    }
    </style>
    """, unsafe_allow_html=True)

top_right = st.empty()
with top_right.container():
    st.markdown('<div class="top-right">', unsafe_allow_html=True)
    if st.session_state.user is None:
        st.write("**Nie jesteś zalogowany**")
        if st.button("Zaloguj się przez Google", key="login_button_app"):
            oauth = OAuth2Session(
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=["openid", "email", "profile"]
            )
            authorization_url, state = oauth.create_authorization_url(AUTHORIZATION_ENDPOINT)
            st.session_state.oauth_state = state
            st.write(f"[Kliknij tutaj aby się zalogować]({authorization_url})")
    else:
        st.write(f"**Zalogowany jako:** {st.session_state.user.get('name', 'User')}")
        if st.button("Wyloguj się", key="logout_button_app"):
            st.session_state.user = None
            st.success("Wylogowano!")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Main App Content ---
st.title("🤖 Witaj w TechFest RAG")
st.markdown("Przejdź do zakładki **Upload** aby dodać pliki PDF, lub do **Chat** żeby rozmawiać.")

if st.button("📤 Przejdź do uploadu"):
    st.switch_page("pages/1_Upload.py")

if st.session_state.user:
    st.write(f"Witaj, {st.session_state.user.get('name', 'User')}!")
