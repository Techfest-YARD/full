import streamlit as st
import requests
from authlib.integrations.requests_client import OAuth2Session
import os

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")


# Make sure to update this redirect URI to match your configuration (it must be registered in Google Console)
REDIRECT_URI = "http://localhost:8080/oauth2callback"  

# OAuth endpoints for Google
AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"

# --- Session State Initialization ---
if "user" not in st.session_state:
    st.session_state.user = None
if "oauth_state" not in st.session_state:
    st.session_state.oauth_state = None

# --- UI ---
st.set_page_config(page_title="Login Panel", layout="centered")
st.title("🔐 Login Panel")
st.write("Login with your Google account to register and sign in.")

if st.session_state.user is None:
    # Show the login button and instructions
    if st.button("Login with Google"):
        # Create an OAuth2 session
        oauth = OAuth2Session(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=["openid", "email", "profile"]
        )
        # Create the authorization URL
        authorization_url, state = oauth.create_authorization_url(AUTHORIZATION_ENDPOINT)
        st.session_state.oauth_state = state
        st.write(f"Click [here]({authorization_url}) to authorize.")
        st.info("After authorizing, copy the 'code' parameter from the URL and paste it below.")
    
    # Text input for the user to paste the authorization code
    code = st.text_input("Enter the authorization code:")
    if code:
        # Re-create the OAuth2 session (it will use the same state)
        oauth = OAuth2Session(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=["openid", "email", "profile"]
        )
        # Fetch the token using the provided code
        token = oauth.fetch_token(TOKEN_ENDPOINT, code=code)
        # Fetch user info
        response = oauth.get(USERINFO_ENDPOINT)
        user_info = response.json()
        st.session_state.user = user_info
        st.success(f"Logged in as: {user_info.get('email')}")
else:
    st.write(f"Welcome, {st.session_state.user.get('name', 'User')}!")
    st.image(st.session_state.user.get("picture"), width=100)
    st.write("You are now logged in.")

# For demonstration purposes, display the user info dictionary
if st.session_state.user:
    st.json(st.session_state.user)
