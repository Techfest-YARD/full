import os
import json
import random
import hashlib
import streamlit as st
import streamlit.components.v1 as components

# --- Configuration ---
FLASHCARD_DIR = "/home/flashacrd"  # Target directory for JSON files

# Inline Git-related context data.
context_data = """
Git is a distributed version control system.
It helps you track changes and collaborate on code.
git init initializes a new repository.
git add stages changes.
git commit records snapshots.
git push sends your changes to a remote repository.
git pull retrieves updates from a remote repository.
git branch lists branches.
git checkout switches branches.
git merge integrates changes from different branches.
"""

# --- Custom CSS for Flashcards ---
st.markdown("""
    <style>
    .flashcard {
        background-color: #0a3d62; 
        color: white;
        font-family: Arial, sans-serif;
        width: 600px;
        height: 300px;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        margin: 20px auto;
        border-radius: 10px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Utility Functions ---

def read_context(dummy_path: str) -> str:
    """
    Instead of reading from a file, return the inline context_data.
    """
    return context_data.strip()

def generate_flashcards(context: str) -> list:
    """
    Uses the provided context to generate up to 20 flashcards.
    Each flashcard is a dict with keys: 'card_id', 'side1', 'side2'.
    For this demo, we assume each sentence is a concept.
    """
    sentences = context.split("\n")
    flashcards = []
    card_id = 1
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and len(flashcards) < 20:
            # For demonstration, use the sentence as both term and definition.
            flashcards.append({
                "card_id": str(card_id),
                "side1": f"Term: {sentence}",
                "side2": f"Definition: {sentence}"
            })
            card_id += 1
    if not flashcards:
        flashcards.append({
            "card_id": "1",
            "side1": "Term: What is a flashcard?",
            "side2": "Definition: A flashcard is a tool for learning."
        })
    return flashcards

def compute_hash(data: list) -> str:
    """
    Computes an MD5 hash for the given data.
    """
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.md5(json_str.encode('utf-8')).hexdigest()

def save_flashcards(data: list, directory: str = FLASHCARD_DIR) -> str:
    """
    Saves the flashcards data as JSON to a file with a hash-based filename.
    Returns the full file path.
    """
    os.makedirs(directory, exist_ok=True)
    json_str = json.dumps(data, sort_keys=True, indent=2)
    md5_hash = compute_hash(data)
    filename = f"set{md5_hash}.json"
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json_str)
    return filepath

def load_flashcards(file_path: str) -> list:
    """
    Loads flashcards from a JSON file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- Streamlit UI Functions ---

def display_flashcards_ui(flashcards: list):
    """
    Displays the flashcards UI, handling card flipping, score,
    and keyboard interactions.
    """
    # Initialize session state variables if not set.
    if 'cards' not in st.session_state:
        st.session_state.cards = flashcards
        random.shuffle(st.session_state.cards)
    if 'current_card' not in st.session_state:
        st.session_state.current_card = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'show_back' not in st.session_state:
        st.session_state.show_back = False

    # Sidebar: display score and progress.
    st.sidebar.markdown(f"### Score: **{st.session_state.score}**")
    st.sidebar.markdown(f"### Progress: **{st.session_state.current_card}/{len(st.session_state.cards)}**")

    if st.session_state.current_card < len(st.session_state.cards):
        card = st.session_state.cards[st.session_state.current_card]
        # Use a div with the flashcard class for styling.
        card_content = card["side2"] if st.session_state.show_back else card["side1"]
        st.markdown(f"<div class='flashcard'>{card_content}</div>", unsafe_allow_html=True)

        # Three columns for buttons, each with unique keys.
        col1, col2, col3 = st.columns(3)
        if col1.button("❌ Reject (Left Arrow)", key=f"reject_{card['card_id']}"):
            st.session_state.current_card += 1
            st.session_state.show_back = False
        if col2.button("🔄 Flip (Space)", key=f"flip_{card['card_id']}"):
            st.session_state.show_back = not st.session_state.show_back
        if col3.button("✅ Accept (Right Arrow)", key=f"accept_{card['card_id']}"):
            st.session_state.score += 1
            st.session_state.current_card += 1
            st.session_state.show_back = False

        # Handle keyboard events using streamlit_javascript (if installed).
        try:
            from streamlit_javascript import st_javascript
            key = st_javascript("document.addEventListener('keydown', e => e.key);")
            if key:
                if key == " ":
                    st.session_state.show_back = not st.session_state.show_back
                elif key == "ArrowRight":
                    st.session_state.score += 1
                    st.session_state.current_card += 1
                    st.session_state.show_back = False
                elif key == "ArrowLeft":
                    st.session_state.current_card += 1
                    st.session_state.show_back = False
        except ImportError:
            st.warning("Install streamlit-javascript (pip install streamlit-javascript) for keyboard support.")
    else:
        # All cards reviewed: show summary dialog.
        st.markdown("## You've finished the flashcards!")
        st.markdown(f"### Your final score: **{st.session_state.score}** out of **{len(st.session_state.cards)}**")
        if st.button("Restart with same set"):
            st.session_state.current_card = 0
            st.session_state.score = 0
            st.session_state.show_back = False
            random.shuffle(st.session_state.cards)
        if st.button("Generate New Flashcards"):
            # Clear session state and re-run the generation pipeline.
            for key in ['cards', 'current_card', 'score', 'show_back']:
                if key in st.session_state:
                    del st.session_state[key]
            run_pipeline()

def run_pipeline():
    """
    The main pipeline:
      1. Get the context from the inline string.
      2. Generate flashcards via a Gemini stub.
      3. Save flashcards with computed hash.
      4. Load flashcards and display the flashcards UI.
    """
    # Get the inline context.
    context = read_context("dummy_path_not_used")
    
    # Generate flashcards using the context.
    flashcards = generate_flashcards(context)
    
    # Save the generated flashcards to a JSON file.
    saved_file = save_flashcards(flashcards)
    st.info(f"Flashcards generated and saved to: {saved_file}")

    # For the UI, load the flashcards from the file.
    try:
        loaded_flashcards = load_flashcards(saved_file)
    except Exception as e:
        st.error(f"Error loading flashcards: {e}")
        return

    # Display the flashcards UI.
    display_flashcards_ui(loaded_flashcards)

# --- Main Application ---
st.set_page_config(page_title="Dynamic Flashcards", page_icon="📚", layout="wide")
st.title("Dynamic Flashcards Application")
st.markdown("This app generates Git-related flashcards from an inline context using a Gemini stub and then displays them for review.")

# Button to start the generation pipeline.
if st.button("Generate Flashcards"):
    # Clear any previous session state.
    for key in ['cards', 'current_card', 'score', 'show_back']:
        if key in st.session_state:
            del st.session_state[key]
    run_pipeline()

# If flashcards have been generated, display them.
if 'cards' in st.session_state:
    display_flashcards_ui(st.session_state.cards)

