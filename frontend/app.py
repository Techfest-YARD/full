import streamlit as st

st.title("My Streamlit App with Google Login")

if not st.experimental_user.is_logged_in:
    st.write("## Please log in")
    st.button("🔐 Log in with Google", on_click=st.login)
    st.stop()

# If logged in, display the app content and user info
user = st.experimental_user
st.success(f"Logged in as: {user.email}")
st.image(user.picture, width=50)
st.write(f"Name: {user.name}")

# Protected content can go here
st.write("...app content...")

# Logout option
if st.button("Log out"):
    st.logout()
