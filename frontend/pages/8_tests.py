import streamlit as st

# Must be the first Streamlit command
st.set_page_config(page_title="GenAI Mock Quiz", page_icon="✅", layout="wide")

# --- Custom CSS to Make the Quiz Look Nice ---
st.markdown("""
<style>
.question-box {
    background-color: #f5f5f5;
    margin: 20px auto;
    padding: 20px;
    border-radius: 10px;
    width: 600px;
}
.answer-box {
    background-color: #ffffff;
    margin: 10px 0;
    padding: 15px;
    border-radius: 5px;
    border: 1px solid #ddd;
}
.explanation-box {
    background-color: #e6f7ff;
    margin: 10px auto;
    padding: 15px;
    border-radius: 5px;
    border: 1px solid #b3e0ff;
    width: 600px;
}
</style>
""", unsafe_allow_html=True)

# --- Mock JSON Data: 5 Questions with Multiple Correct Answers ---
MOCK_QUESTIONS = [
    {
        "Question": "1. What is Git?",
        "AnswerA": "A type of programming language",
        "AnswerB": "A distributed version control system",
        "AnswerC": "A code linter for Python",
        "AnswerD": "A task scheduling tool",
        "CorrectAnswers": ["B"],
        "Explanation": "Git is a distributed version control system."
    },
    {
        "Question": "2. Which of the following are Git commands?",
        "AnswerA": "git commit",
        "AnswerB": "npm install",
        "AnswerC": "git push",
        "AnswerD": "apt-get update",
        "CorrectAnswers": ["A", "C"],
        "Explanation": "'git commit' and 'git push' are valid Git commands. The others belong to different tools."
    },
    {
        "Question": "3. Which statements are true about Git branching?",
        "AnswerA": "Branches allow you to work on different features in parallel",
        "AnswerB": "You can only have one branch at a time",
        "AnswerC": "Merging branches lets you integrate changes",
        "AnswerD": "Branches are always stored remotely",
        "CorrectAnswers": ["A", "C"],
        "Explanation": "Branches are local by default and can be used in parallel. Merging integrates changes from one branch into another."
    },
    {
        "Question": "4. Which Git command shows the history of commits?",
        "AnswerA": "git status",
        "AnswerB": "git log",
        "AnswerC": "git revert",
        "AnswerD": "git show",
        "CorrectAnswers": ["B"],
        "Explanation": "'git log' displays the commit history."
    },
    {
        "Question": "5. Which of the following could happen if you never commit your changes?",
        "AnswerA": "You might lose important modifications if you switch branches",
        "AnswerB": "All changes are automatically tracked and saved",
        "AnswerC": "Your changes won't be in the repository history",
        "AnswerD": "You can't stage new changes",
        "CorrectAnswers": ["A", "C"],
        "Explanation": "Without commits, you can lose work by switching branches and your changes won't be recorded in the repo's history."
    }
]

# --- Session State Initialization ---
if "user_answers" not in st.session_state:
    # Create an empty dict to hold user answers for each question
    st.session_state.user_answers = {str(i): set() for i in range(len(MOCK_QUESTIONS))}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False


def display_question(question_data: dict, index: int):
    """
    Display a single question in a rectangular box, along with four checkboxes
    for possible answers. The user can select multiple answers.
    """
    question_id = str(index)
    st.markdown(f"<div class='question-box'><strong>{question_data['Question']}</strong></div>", unsafe_allow_html=True)
    
    # Display 4 answer options in rectangular fields
    answer_col = st.container()
    with answer_col:
        # For each answer, we create a unique key. The user can select multiple answers
        # so we store them in st.session_state.user_answers[question_id] as a set of strings.
        for letter in ["A", "B", "C", "D"]:
            answer_text = question_data[f"Answer{letter}"]
            # Create a checkbox
            checked = letter in st.session_state.user_answers[question_id]
            new_val = st.checkbox(
                f"{letter}. {answer_text}",
                key=f"q{question_id}_ans{letter}",
                value=checked
            )
            # If checked, add it to the set of user answers; else remove
            if new_val:
                st.session_state.user_answers[question_id].add(letter)
            else:
                st.session_state.user_answers[question_id].discard(letter)


def display_quiz(questions: list):
    """
    Display all questions. 
    If the quiz is already submitted, show the summary.
    """
    # If the quiz hasn't been submitted yet, display each question
    if not st.session_state.quiz_submitted:
        st.header("Multiple-Choice Quiz")
        st.write("Select the correct answers for each question below:")
        for i, q in enumerate(questions):
            display_question(q, i)
        
        if st.button("Submit Answers"):
            st.session_state.quiz_submitted = True
    else:
        # Show summary
        display_summary(questions)


def display_summary(questions: list):
    """
    Display the final summary, showing each question with correct answers, 
    the user's choices, and explanations.
    """
    st.header("Quiz Summary")
    correct_count = 0
    total_questions = len(questions)
    
    for i, q in enumerate(questions):
        question_id = str(i)
        user_choices = sorted(list(st.session_state.user_answers[question_id]))
        correct_choices = sorted(list(q["CorrectAnswers"]))
        # Check if user is correct
        if user_choices == correct_choices:
            correct_count += 1
        
        # Show the question in a box
        st.markdown(f"<div class='question-box'><strong>{q['Question']}</strong></div>", unsafe_allow_html=True)
        st.write(f"**Your answers:** {user_choices if user_choices else 'No selection'}")
        st.write(f"**Correct answers:** {correct_choices}")
        
        # Explanation in a separate box
        st.markdown(f"<div class='explanation-box'><strong>Explanation:</strong> {q['Explanation']}</div>", unsafe_allow_html=True)
    
    st.write(f"**You got {correct_count} out of {total_questions} questions correct.**")
    
    # Button to let user reset and do it again
    if st.button("Try Again"):
        for k in ["user_answers", "quiz_submitted"]:
            if k in st.session_state:
                del st.session_state[k]
        # Force immediate rerun
        st.experimental_rerun()


# --- MAIN PAGE ---
st.title("GenAI Mock Quiz")
st.write("""
A short multiple-choice test generated from a fixed mock dataset.
Select all correct answers for each question, then click "Submit Answers" 
to see your summary and explanations.
""")

display_quiz(MOCK_QUESTIONS)
