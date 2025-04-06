import streamlit as st
import os
import requests
from authlib.integrations.requests_client import OAuth2Session

# Must be the very first Streamlit command!
st.set_page_config(page_title="TechFest RAG", page_icon="🤖", layout="wide")

# --- OAuth Configuration (using environment variables) ---
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

# --- Automatic Code Retrieval / Mocking for Google OAuth ---
query_params = st.query_params  # st.query_params is a property
if "code" in query_params and st.session_state.user is None:
    code = query_params["code"][0]
    st.write("Debug: Found code in query params (mock mode):", code)
    try:
        oauth = OAuth2Session(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=["openid", "email", "profile"]
        )
        token = oauth.fetch_token(TOKEN_ENDPOINT, code=code)
        st.write("Debug: Token fetched:", token)
        response = oauth.get(USERINFO_ENDPOINT)
        user_info = response.json()
        st.write("Debug: User info retrieved:", user_info)
        st.session_state.user = user_info
        # Optionally update the URL to indicate login status.
        st.set_query_params(logged_in="true")
        st.experimental_rerun()  # Force a rerun so that the UI updates.
    except Exception as e:
        st.error("Error during OAuth token retrieval: " + str(e))
        st.set_query_params()

# --- Top-Right Permanent Google OAuth Login/Logout Panel ---
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
            # Use an anchor tag with target="_self" to force same-window navigation.
            login_link = f'<a href="{authorization_url}" target="_self">Kliknij tutaj aby się zalogować</a>'
            st.markdown(login_link, unsafe_allow_html=True)
    else:
        st.write(f"**Zalogowany jako:** {st.session_state.user.get('name', 'User')}")
        if st.button("Wyloguj się", key="logout_button_app"):
            st.session_state.user = None
            st.set_query_params()  # Clear query parameters.
            st.success("Wylogowano!")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Additional Hardcoded Credentials Login Panel ---
st.markdown("""
    <style>
    .credentials-login {
        background-color: #fff;
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        width: 400px;
        margin: 20px auto;
        font-family: Arial, sans-serif;
        text-align: center;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='credentials-login'><h3>Logowanie (Kredencje)</h3>", unsafe_allow_html=True)
    username = st.text_input("Login", key="cred_username")
    password = st.text_input("Hasło", type="password", key="cred_password")
    if st.button("Zaloguj (Kredencje)", key="cred_login"):
        if username == "Suser" and password == "Su":
            st.session_state.user = {
                "name": "Suser",
                "role": "Super User",
                "email": "suser@example.com",
                "picture": "https://via.placeholder.com/150"
            }
            st.success("Zalogowano jako Super User")
            st.experimental_rerun()
        elif username == "Użytkownik" and password == "u":
            st.session_state.user = {
                "name": "Użytkownik",
                "role": "Użytkownik",
                "email": "uzytkownik@example.com",
                "picture": "https://via.placeholder.com/150"
            }
            st.success("Zalogowano jako Użytkownik")
            st.experimental_rerun()
        else:
            st.error("Nieprawidłowe dane logowania.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Main App Content ---
st.title("🤖 Witaj w TechFest RAG")
st.markdown("Przejdź do zakładki **Upload** aby dodać pliki PDF, lub do **Chat** żeby rozmawiać.")

if st.button("📤 Przejdź do uploadu"):
    st.switch_page("1_Upload")

if st.session_state.user:
    st.write(f"Witaj, {st.session_state.user.get('name', 'User')}! Role: {st.session_state.user.get('role', 'N/A')}")
else:
    st.write("Nie jesteś zalogowany.")

# --- Debug Section (Optional) ---
with st.expander("Debug Info", expanded=False):
    st.write("Query Parameters:", st.query_params)
    st.write("Session State:", st.session_state)
