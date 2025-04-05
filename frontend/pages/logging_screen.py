import streamlit as st
import requests
from authlib.integrations.requests_client import OAuth2Session
import os

# OAuth configuration (secrets stored in environment variables)
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
# This redirect URI must match what you set up in the Google Console
REDIRECT_URI = "https://frontend-46193761155.europe-west3.run.app/oauth2callback"  
AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"

# --- Session State Initialization ---
if "user" not in st.session_state:
    st.session_state.user = None
if "oauth_state" not in st.session_state:
    st.session_state.oauth_state = None

# Set up the main app content.
st.set_page_config(page_title="Login Panel", layout="centered")
st.title("Main App Content")
st.write("This is your main application. Use the top-right panel to log in or out.")

# --- Top-Right Permanent Login/Logout Panel Styling ---
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

# --- Automatic Code Retrieval from URL ---
query_params = st.experimental_get_query_params()
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
    # Clear query parameters to avoid re-processing on refresh.
    st.experimental_set_query_params()

# --- Top-Right Login/Logout Panel ---
top_right = st.empty()
with top_right.container():
    st.markdown('<div class="top-right">', unsafe_allow_html=True)
    if st.session_state.user is None:
        st.write("**Not logged in**")
        if st.button("Login with Google", key="login_button"):
            oauth = OAuth2Session(
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=["openid", "email", "profile"]
            )
            authorization_url, state = oauth.create_authorization_url(AUTHORIZATION_ENDPOINT)
            st.session_state.oauth_state = state
            st.write(f"[Click here to authorize]({authorization_url})")
    else:
        st.write(f"**Logged in as:** {st.session_state.user.get('name', 'User')}")
        if st.button("Logout", key="logout_button"):
            st.session_state.user = None
            st.success("Logged out!")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Main Page Content Display ---
if st.session_state.user:
    st.write(f"Welcome, {st.session_state.user.get('name', 'User')}!")
    st.image(st.session_state.user.get("picture"), width=100)
    st.json(st.session_state.user)
else:
    st.write("Please log in using the top-right panel.")
