import streamlit as st
import json
import logging

# Configure the page – must be first!
st.set_page_config(page_title="GenAI Test Quiz", page_icon="✅", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
.question-box {
    background-color: #f5f5f5;
    margin: 20px auto;
    padding: 20px;
    border-radius: 10px;
    width: 600px;
    text-align: center;
    font-family: Arial, sans-serif;
}
.explanation-box {
    background-color: #e6f7ff;
    margin: 10px auto;
    padding: 15px;
    border-radius: 5px;
    border: 1px solid #b3e0ff;
    width: 600px;
    font-family: Arial, sans-serif;
}
</style>
""", unsafe_allow_html=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- Mock Test Data (Hard-Coded) ---
MOCK_TEST = [
    {
        "Question": "What is Git?",
        "AnswerA": "A distributed version control system",
        "AnswerB": "A programming language",
        "AnswerC": "A text editor",
        "AnswerD": "A web framework",
        "CorrectAnswer": "A",
        "Explanation": "Git is a distributed version control system used to track changes in source code."
    },
    {
        "Question": "Which command is used to initialize a new Git repository?",
        "AnswerA": "git commit",
        "AnswerB": "git init",
        "AnswerC": "git clone",
        "AnswerD": "git status",
        "CorrectAnswer": "B",
        "Explanation": "The 'git init' command is used to create a new Git repository."
    },
    {
        "Question": "How do you add files to the staging area in Git?",
        "AnswerA": "git add",
        "AnswerB": "git commit",
        "AnswerC": "git push",
        "AnswerD": "git pull",
        "CorrectAnswer": "A",
        "Explanation": "The 'git add' command stages changes to be committed."
    },
    {
        "Question": "Which command shows the commit history?",
        "AnswerA": "git log",
        "AnswerB": "git status",
        "AnswerC": "git branch",
        "AnswerD": "git diff",
        "CorrectAnswer": "A",
        "Explanation": "The 'git log' command displays the commit history."
    },
    {
        "Question": "Which command is used to merge branches in Git?",
        "AnswerA": "git commit",
        "AnswerB": "git merge",
        "AnswerC": "git branch",
        "AnswerD": "git init",
        "CorrectAnswer": "B",
        "Explanation": "The 'git merge' command is used to integrate changes from one branch into another."
    }
]

# --- Session State Initialization ---
if "test_questions" not in st.session_state:
    st.session_state.test_questions = None
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

def generate_test():
    """Mock the generation of a test by storing the hard-coded questions."""
    st.session_state.test_questions = MOCK_TEST
    # Initialize each question answer as None.
    for i in range(len(MOCK_TEST)):
        st.session_state.user_answers[str(i)] = None

def display_test_generation():
    """
    Interface to generate the test. The user may enter a prompt (or use the default)
    and click the button to generate the test.
    """
    st.header("Generate a Test")
    prompt = st.text_input("Enter a prompt for generating the test:",
                           value="Please generate a multiple-choice test on Git.")
    if st.button("Generate Test"):
        generate_test()
        st.experimental_rerun()

def display_question(question_data, index: int):
    """
    Displays a single question in a fixed rectangular box with the question text,
    and below that a radio button list with 4 answer options.
    """
    question_id = str(index)
    st.markdown(
        f"<div class='question-box'><strong>{question_data['Question']}</strong></div>", 
        unsafe_allow_html=True
    )
    options = {
        "A": question_data.get("AnswerA", ""),
        "B": question_data.get("AnswerB", ""),
        "C": question_data.get("AnswerC", ""),
        "D": question_data.get("AnswerD", "")
    }
    selected = st.radio(
        f"Select one answer for question {index+1}:",
        options=list(options.keys()),
        format_func=lambda x: f"{x}. {options[x]}",
        key=f"question_{question_id}"
    )
    st.session_state.user_answers[question_id] = selected

def display_quiz(questions: list):
    """
    If the quiz hasn't been submitted, display all questions.
    Once submitted, display a summary with results.
    """
    if not st.session_state.quiz_submitted:
        st.header("Multiple-Choice Quiz")
        st.write("Select the correct answer for each question:")
        for i, q in enumerate(questions):
            display_question(q, i)
        if st.button("Submit Answers"):
            st.session_state.quiz_submitted = True
            st.experimental_rerun()
    else:
        display_summary(questions)

def display_summary(questions: list):
    """
    Displays the quiz summary: For each question, shows the question,
    the user's answer, the correct answer, and the explanation.
    """
    st.header("Quiz Summary")
    correct_count = 0
    total_questions = len(questions)
    for i, q in enumerate(questions):
        question_id = str(i)
        user_choice = st.session_state.user_answers.get(question_id, "No answer")
        correct_choice = q.get("CorrectAnswer", "N/A")
        if user_choice == correct_choice:
            correct_count += 1
        st.markdown(
            f"<div class='question-box'><strong>{q['Question']}</strong></div>", 
            unsafe_allow_html=True
        )
        st.write(f"**Your answer:** {user_choice} ({q.get('Answer' + user_choice, '')})")
        st.write(f"**Correct answer:** {correct_choice} ({q.get('Answer' + correct_choice, '')})")
        st.markdown(
            f"<div class='explanation-box'><strong>Explanation:</strong> {q.get('Explanation', '')}</div>", 
            unsafe_allow_html=True
        )
    st.write(f"**You got {correct_count} out of {total_questions} questions correct.**")
    if st.button("Try Again"):
        for key in ["test_questions", "user_answers", "quiz_submitted"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()

# --- MAIN PAGE ---
st.title("GenAI Test Quiz")
st.write("""
This test is generated in real-time by a GenAI tool (mocked for this demo).
Click "Generate Test" to fetch a multiple-choice test on Git,
then answer the questions and view your results.
""")

if st.session_state.test_questions is None:
    display_test_generation()
else:
    display_quiz(st.session_state.test_questions)
