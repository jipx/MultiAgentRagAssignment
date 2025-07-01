import streamlit as st
import json
import os
import difflib
import datetime
import pandas as pd

# --- Theme Toggle ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

toggle = st.sidebar.radio("Theme Mode", ["🌞 Light", "🌙 Dark"])
st.session_state.theme = 'dark' if toggle == "🌙 Dark" else 'light'

light_css = """
<style>
body {
    background-color: #ffffff;
    color: #000000;
}
</style>
"""

dark_css = """
<style>
body {
    background-color: #1e1e1e;
    color: #f5f5f5;
}
code, pre {
    background-color: #333 !important;
}
</style>
"""

st.markdown(dark_css if st.session_state.theme == 'dark' else light_css, unsafe_allow_html=True)

# --- Helper Functions ---
def get_filename(prefix, lab, step, ext):
    base_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(base_dir, exist_ok=True)
    filename = f"{prefix}_{lab.lower().replace(' ', '_')}_{step.lower().replace(' ', '_')}.{ext}"
    return os.path.join(base_dir, filename)

def load_file_content(filepath, default_text):
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except FileNotFoundError:
        return default_text

def load_quiz_data(filepath):
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"questions": []}

# --- Sidebar Navigation ---
st.sidebar.title("Lab Navigation")
page = st.sidebar.selectbox("Select a page", ["Lab Tabs", "Student Upload", "Lecturer View"])
lab_choice = st.sidebar.selectbox("Select Lab", ["Lab 1", "Lab 2"])
step_choice = st.sidebar.selectbox("Select Step", ["Step 1", "Step 2"])

# --- File Upload ---
st.sidebar.title("Upload Files")
uploaded_labnotes = st.sidebar.file_uploader("Upload Lab Notes", type="txt")
uploaded_quiz = st.sidebar.file_uploader("Upload Quiz (JSON)", type="json")
uploaded_solution = st.sidebar.file_uploader("Upload Solution", type="txt")
uploaded_original = st.sidebar.file_uploader("Upload Original Code", type="txt")

# --- Save Uploaded Files ---
if uploaded_labnotes:
    with open(get_filename("labnotes", lab_choice, step_choice, "txt"), "wb") as f:
        f.write(uploaded_labnotes.read())
if uploaded_quiz:
    with open(get_filename("quiz", lab_choice, step_choice, "json"), "wb") as f:
        f.write(uploaded_quiz.read())
if uploaded_solution:
    with open(get_filename("solution", lab_choice, step_choice, "txt"), "wb") as f:
        f.write(uploaded_solution.read())
if uploaded_original:
    with open(get_filename("original", lab_choice, step_choice, "txt"), "wb") as f:
        f.write(uploaded_original.read())

# --- Page: Lab Tabs ---
if page == "Lab Tabs":
    tabs = st.tabs(["Lab", "Hint", "Quiz", "Solution", "Lab Score"])

    with tabs[0]:
        st.header("Lab Content")
        lab_file = get_filename("labnotes", lab_choice, step_choice, "txt")
        lab_notes = load_file_content(lab_file, "Lab notes not found.")
        st.markdown(lab_notes)

    with tabs[1]:
        st.header("Hint")
        st.write(f"Hints for **{lab_choice} - {step_choice}**")
        st.text_area("Hint Details", height=150)

    with tabs[2]:
        st.header("🧠 Quiz")

        quiz_file = get_filename("quiz", lab_choice, step_choice, "json")
        quiz_data = load_quiz_data(quiz_file)
        questions = quiz_data.get("questions", [])

        if questions:
            if 'quiz_index' not in st.session_state:
                st.session_state.quiz_index = 0
            if 'score' not in st.session_state:
                st.session_state.score = 0
            if 'answered' not in st.session_state:
                st.session_state.answered = [False] * len(questions)

            q_index = st.session_state.quiz_index
            q = questions[q_index]

            st.progress((q_index + 1) / len(questions))

            st.markdown(f"""
            <div style="background-color:#f0f2f6;padding:15px;border-radius:10px;margin-bottom:10px;">
                <h4 style="color:#1a73e8;">Question {q_index + 1} of {len(questions)}</h4>
                <p style="font-size:17px;">{q["question"]}</p>
            </div>
            """, unsafe_allow_html=True)

            selected_choice = st.radio("Choices", q.get("choices", []), key=q_index)

            if st.button("Submit Answer") and not st.session_state.answered[q_index]:
                correct = q.get("answer", "").strip().lower()
                submitted = selected_choice.strip().lower()

                if submitted == correct:
                    st.success("✅ Correct answer!")
                    st.session_state.score += 1
                else:
                    st.error(f"❌ Incorrect. Correct answer: {q['answer']}")
                if "explanation" in q:
                    st.info(f"ℹ️ Explanation: {q['explanation']}")

                st.session_state.answered[q_index] = True

            if q_index < len(questions) - 1:
                if st.button("Next Question"):
                    st.session_state.quiz_index += 1
            else:
                st.success(f"🎉 Quiz Completed! Score: {st.session_state.score} / {len(questions)}")
                if st.button("Restart Quiz"):
                    st.session_state.quiz_index = 0
                    st.session_state.score = 0
                    st.session_state.answered = [False] * len(questions)
        else:
            st.info("No quiz questions found.")

    with tabs[3]:
        st.header("🔍 Code Difference (Unified View)")

        solution_file = get_filename("solution", lab_choice, step_choice, "txt")
        original_file = get_filename("original", lab_choice, step_choice, "txt")
        solution = load_file_content(solution_file, "Solution not available.").splitlines()
        original = load_file_content(original_file, "Original code not available.").splitlines()

        diff_lines = difflib.unified_diff(
            original,
            solution,
            fromfile="Original Code",
            tofile="Solution Code",
            lineterm=""
        )
        diff_text = "\n".join(diff_lines)

        if diff_text.strip():
            st.code(diff_text, language="diff")

            st.subheader("💬 Reviewer Comment")
            user_comment = st.text_area("Leave your feedback:", height=150)

            if st.button("💾 Save Comment"):
                comments_dir = os.path.join(os.getcwd(), 'comments')
                os.makedirs(comments_dir, exist_ok=True)
                comment_path = os.path.join(
                    comments_dir,
                    f'comment_{lab_choice.lower().replace(" ", "_")}_{step_choice.lower().replace(" ", "_")}.txt'
                )
                with open(comment_path, "w", encoding="utf-8") as f:
                    f.write(user_comment)
                st.success("✅ Comment saved.")
        else:
            st.success("✅ No differences found between original and solution.")

    with tabs[4]:
        st.header("Lab Score")
        if 'score' in st.session_state and 'answered' in st.session_state:
            total = len(st.session_state.answered)
            completed = sum(1 for a in st.session_state.answered if a)
            st.metric(label="Questions Completed", value=completed)
            st.metric(label="Score", value=f"{st.session_state.score} / {total}")
        else:
            st.info("Score will appear after quiz interaction.")

# The rest (Student Upload and Lecturer View) continues unchanged.
