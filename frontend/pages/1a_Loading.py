import streamlit as st

# Initialize session state for uploaded files if not already present
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

st.title("📄 Document Management")

# File uploader allows multiple files to be uploaded
uploaded_files = st.file_uploader("Upload your documents", accept_multiple_files=True)

# Mock processing of uploaded files
if uploaded_files:
    for uploaded_file in uploaded_files:
        # Check if the file is already in the list to avoid duplicates
        if uploaded_file.name not in [file['name'] for file in st.session_state.uploaded_files]:
            # Mock processing time
            with st.spinner(f"Processing {uploaded_file.name}..."):
                import time
                time.sleep(2)  # Simulate processing time
            # Add file to session state
            st.session_state.uploaded_files.append({"name": uploaded_file.name})
            st.success(f"{uploaded_file.name} uploaded successfully!")

# Display the list of uploaded documents
st.subheader("Uploaded Documents")
if st.session_state.uploaded_files:
    for file in st.session_state.uploaded_files:
        col1, col2 = st.columns([0.8, 0.2])
        col1.write(f"📄 {file['name']}")
        # Create a button with a unique key for each file to delete it from the list
        if col2.button("Delete", key=file['name']):
            st.session_state.uploaded_files.remove(file)
            st.experimental_rerun()
else:
    st.info("No documents uploaded yet.")

