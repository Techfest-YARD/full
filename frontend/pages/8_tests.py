import streamlit as st
import logging

# Configure the page
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
        "Question": "Which of the following are Git commands?",
        "AnswerA": "git clone",
        "AnswerB": "git push",
        "AnswerC": "git deploy",
        "AnswerD": "git merge",
        "CorrectAnswers": ["A", "B", "D"],
        "Explanation": "git clone, git push, and git merge are valid Git commands. 'git deploy' is not a standard Git command."
    },
    {
        "Question": "What can you do with Git branches?",
        "AnswerA": "Create multiple lines of development",
        "AnswerB": "Delete production history",
        "AnswerC": "Switch between features",
        "AnswerD": "Combine features",
        "CorrectAnswers": ["A", "C", "D"],
        "Explanation": "Branches allow for parallel development, switching contexts, and merging features back together."
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
    st.session_state.test_questions = MOCK_TEST
    for i in range(len(MOCK_TEST)):
        st.session_state.user_answers[str(i)] = []

def display_test_generation():
    st.header("Generate a Test")
    prompt = st.text_input("Enter a prompt for generating the test:",
                           value="Please generate a multiple-choice test on Git.")
    if st.button("Generate Test"):
        generate_test()
        st.rerun()

def display_question(question_data, index: int):
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
    selected = st.multiselect(
        f"Select one or more answers for question {index+1}:",
        options=list(options.keys()),
        format_func=lambda x: f"{x}. {options[x]}",
        key=f"question_{question_id}"
    )
    st.session_state.user_answers[question_id] = selected

def display_quiz(questions: list):
    if not st.session_state.quiz_submitted:
        st.header("Multiple-Choice Quiz")
        st.write("Select the correct answer(s) for each question:")
        for i, q in enumerate(questions):
            display_question(q, i)
        if st.button("Submit Answers"):
            st.session_state.quiz_submitted = True
            st.rerun()
    else:
        display_summary(questions)

def display_summary(questions: list):
    st.header("Quiz Summary")
    correct_count = 0
    total_questions = len(questions)
    for i, q in enumerate(questions):
        question_id = str(i)
        user_choices = set(st.session_state.user_answers.get(question_id, []))
        correct_choices = set(q.get("CorrectAnswers", []))
        if user_choices == correct_choices:
            correct_count += 1
        st.markdown(
            f"<div class='question-box'><strong>{q['Question']}</strong></div>", 
            unsafe_allow_html=True
        )
        st.write(f"**Your answer(s):** {', '.join(user_choices)}")
        st.write(f"**Correct answer(s):** {', '.join(correct_choices)}")
        st.markdown(
            f"<div class='explanation-box'><strong>Explanation:</strong> {q.get('Explanation', '')}</div>", 
            unsafe_allow_html=True
        )
    st.write(f"**You got {correct_count} out of {total_questions} questions correct.**")
    if st.button("Try Again"):
        for key in ["test_questions", "user_answers", "quiz_submitted"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

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
