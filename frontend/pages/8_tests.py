import streamlit as st
import json
import logging
from connectors.ApiBackend import ApiBackend  # Upewnij się, że ścieżka jest poprawna

# Konfiguracja strony
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Inicjalizacja serwisu backendowego
backend = ApiBackend()

# --- Inicjalizacja stanu sesji ---
if "test_questions" not in st.session_state:
    st.session_state.test_questions = None
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

def generate_test_from_backend():
    test_questions = backend.generate_test()
    # Jeśli otrzymany wynik jest ciągiem znaków, sprawdź czy nie jest pusty
    if isinstance(test_questions, str):
        if test_questions.strip() == "":
            st.error("Otrzymano pusty ciąg testowych pytań.")
            test_questions = []
        else:
            try:
                test_questions = json.loads(test_questions)
            except Exception as e:
                st.error("Nie udało się sparsować pytań testowych: " + str(e))
                test_questions = []
    st.session_state.test_questions = test_questions
    # Inicjalizacja odpowiedzi dla każdego pytania (jako None)
    for i in range(len(test_questions)):
        st.session_state.user_answers[str(i)] = None

def display_test_generation():
    """
    Interfejs generowania testu – użytkownik wpisuje prompt lub korzysta z domyślnego,
    a po kliknięciu przycisku wywoływana jest funkcja generująca test.
    """
    st.header("Generate a Test")
    prompt = st.text_input("Enter a prompt for generating the test:",
                           value="Please generate a multiple-choice test on Git.")
    if st.button("Generate Test"):
        generate_test_from_backend()
        st.rerun()

def display_question(question_data, index: int):
    """
    Wyświetla pojedyncze pytanie wraz z opcjami odpowiedzi.
    Jeśli question_data jest ciągiem, próbuje go sparsować jako JSON.
    """
    # Jeśli question_data jest stringiem i nie jest pusty, spróbuj sparsować
    if isinstance(question_data, str):
        if question_data.strip() == "":
            st.error("Pytanie jest puste.")
            return
        try:
            question_data = json.loads(question_data)
        except Exception as e:
            st.error(f"Nie udało się sparsować pytania: {e}")
            return

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
    Jeśli quiz nie został przesłany, wyświetla wszystkie pytania.
    Po przesłaniu wyświetla podsumowanie.
    """
    if not st.session_state.quiz_submitted:
        st.header("Multiple-Choice Quiz")
        st.write("Select the correct answer for each question below:")
        for i, q in enumerate(questions):
            display_question(q, i)
        if st.button("Submit Answers"):
            st.session_state.quiz_submitted = True
            st.rerun()
    else:
        display_summary(questions)

def display_summary(questions: list):
    """
    Wyświetla podsumowanie quizu z wynikami – dla każdego pytania pokazuje odpowiedź użytkownika,
    poprawną odpowiedź oraz wyjaśnienie.
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
        st.rerun()

# --- MAIN PAGE ---
st.title("GenAI Test Quiz")
st.write("""
This test is generated in real-time by an AI model.
Click "Generate Test" to fetch a multiple-choice test from the backend,
then answer the questions and view your results.
""")

if st.session_state.test_questions is None:
    display_test_generation()
else:
    display_quiz(st.session_state.test_questions)
