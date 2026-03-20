import streamlit as st
import time
from datetime import datetime
from components.question_loader import QuestionLoader
from components.timer import Timer
from components.navigation import Navigation
from components.results import Results
from utils.analytics import Analytics
from streamlit_autorefresh import st_autorefresh

# Page config
st.set_page_config(
    page_title="AEM Assets Expert Exam Simulator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .question-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    .progress-bar {
        height: 10px;
        background: #e0e0e0;
        border-radius: 5px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4caf50, #2196f3);
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    defaults = {
        'authenticated': False,
        'mode': None,
        'questions': [],
        'current_question': 0,
        'answers': {},
        'marked_for_review': set(),
        'start_time': None,
        'timer_start': None,
        'time_remaining': 6000,  # 100 mins
        'exam_submitted': False,
        'show_results': False,
        'results': None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_exam_state(clear_results=True):
    keys = [
        'mode', 'questions', 'current_question', 'answers', 'marked_for_review',
        'start_time', 'timer_start', 'time_remaining', 'exam_submitted', 'show_results'
    ]
    if clear_results:
        keys.append('results')
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]
    initialize_session_state()

def show_login():
    st.markdown("""
    <div class="main-header">
        <h1>🔐 Login Page</h1>
        <h3>Please enter your credentials</h3>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        if submit:
            if username == "Supriya" and password == "Loveyoujanmejay":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid username or password")

def start_mode(question_loader, mode: str):
    reset_exam_state(clear_results=True)
    st.session_state.mode = mode
    st.session_state.current_question = 0
    st.session_state.answers = {}
    st.session_state.marked_for_review = set()
    st.session_state.exam_submitted = False
    st.session_state.show_results = False
    st.session_state.start_time = datetime.now()

    if mode == 'practice':
        st.session_state.questions = question_loader.load_questions(shuffle=True)
    else:
        st.session_state.questions = question_loader.load_questions(shuffle=True, limit=100)
        st.session_state.time_remaining = 6000
        st.session_state.timer_start = time.time()

    if not st.session_state.questions:
        st.error("No questions loaded. Please check data/questions_db.json format/path.")
        st.session_state.mode = None
        return

    st.rerun()

def show_mode_selection(question_loader):
    st.markdown("## 📚 Select Exam Mode")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🎯 Practice Mode
        - Unlimited time
        - Immediate feedback
        - Review correct answers
        """)
        if st.button("Start Practice Mode", type="primary", use_container_width=True):
            start_mode(question_loader, 'practice')

    with col2:
        st.markdown("""
        ### ⏰ Exam Mode
        - 100-minute timer
        - 100 questions
        - No immediate feedback
        """)
        if st.button("Start Exam Mode", use_container_width=True):
            start_mode(question_loader, 'exam')

    st.markdown("---")
    st.markdown("### 📊 Question Bank Statistics")
    total_questions = question_loader.get_total_questions()
    topics = question_loader.get_topics()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Questions", total_questions)
    c2.metric("Topics Covered", len(topics))
    c3.metric("Difficulty Levels", "Easy, Medium, Hard")

def show_question():
    q_idx = st.session_state.current_question
    question = st.session_state.questions[q_idx]
    current_answer = st.session_state.answers.get(q_idx)

    st.markdown(f"""
    <div class="question-container">
        <h3>Question {q_idx + 1}</h3>
        <p><strong>{question['question']}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    selection = st.radio(
        "Choose your answer:",
        options=list(range(len(question['options']))),
        index=current_answer if current_answer is not None else None,
        format_func=lambda i: f"{chr(65+i)}) {question['options'][i]}",
        key=f"answer_radio_q_{q_idx}"
    )
    if selection is not None:
        st.session_state.answers[q_idx] = selection

    if st.session_state.mode == 'practice' and selection is not None:
        correct = question['correct']
        if selection == correct:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect. Correct answer is {chr(65 + correct)}")
        st.info(f"💡 **Explanation:** {question['explanation']}")

def show_exam_interface(timer, navigation):
    if not st.session_state.questions:
        st.error("Question set is empty.")
        if st.button("⬅️ Return to Mode Selection"):
            reset_exam_state(clear_results=True)
            st.rerun()
        return

    # timer + progress
    col1, col2 = st.columns([3, 1])
    with col1:
        total = len(st.session_state.questions)
        current = st.session_state.current_question + 1
        progress = current / total
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress*100}%"></div>
        </div>
        <p>Question {current} of {total}</p>
        """, unsafe_allow_html=True)

    with col2:
        if st.session_state.mode == 'exam':
            st_autorefresh(interval=1000, key="exam_timer_refresh")
            timer.show_timer()

    with st.sidebar:
        navigation.show_navigation()
        st.markdown("### 🎮 Controls")
        if st.button("⬅️ Back to Home", use_container_width=True):
            reset_exam_state(clear_results=True)
            st.rerun()

        if st.button("⭐ Mark for Review", use_container_width=True):
            q = st.session_state.current_question
            if q in st.session_state.marked_for_review:
                st.session_state.marked_for_review.remove(q)
            else:
                st.session_state.marked_for_review.add(q)
            st.rerun()

        if st.button("🔄 Reset Current Answer", use_container_width=True):
            q = st.session_state.current_question
            if q in st.session_state.answers:
                del st.session_state.answers[q]
            st.rerun()

        st.markdown("---")
        if st.button("✅ Submit Exam", type="primary", use_container_width=True):
            submit_exam()

    show_question()

    c1, _, c3 = st.columns([1, 2, 1])
    with c1:
        if st.session_state.current_question > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.current_question -= 1
                st.rerun()
    with c3:
        if st.session_state.current_question < len(st.session_state.questions) - 1:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.current_question += 1
                st.rerun()

def submit_exam():
    st.session_state.exam_submitted = True
    st.session_state.show_results = True
    analytics = Analytics()
    st.session_state.results = analytics.calculate_results(
        st.session_state.questions,
        st.session_state.answers
    )
    st.rerun()

def main():
    initialize_session_state()

    if not st.session_state.authenticated:
        show_login()
        return

    question_loader = QuestionLoader()
    timer = Timer()
    navigation = Navigation()
    results = Results()

    st.markdown("""
    <div class="main-header">
        <h1>🎯 AEM Assets Mock</h1>
        <h3>Just for You Supriya❤️</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.mode is None:
        show_mode_selection(question_loader)
    elif st.session_state.mode in ['practice', 'exam'] and not st.session_state.show_results:
        show_exam_interface(timer, navigation)
    elif st.session_state.show_results:
        results.show_results()

if __name__ == "__main__":
    main()
