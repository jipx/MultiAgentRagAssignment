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

import streamlit as st
import json
import os
import difflib
import datetime
import pandas as pd

# --- Helper Functions ---
def get_filename(prefix, lab, step, ext):
    return f"data/{prefix}_{lab.lower().replace(' ', '_')}_{step.lower().replace(' ', '_')}.{ext}"

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
os.makedirs("data", exist_ok=True)
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
                    st.markdown('<div style="background-color:#d4edda;padding:10px;border-radius:8px;color:#155724;">✅ Correct answer!</div>', unsafe_allow_html=True)
                    st.session_state.score += 1
                else:
                    st.markdown(f'<div style="background-color:#f8d7da;padding:10px;border-radius:8px;color:#721c24;">❌ Incorrect. Correct answer: <b>{q["answer"]}</b></div>', unsafe_allow_html=True)

                if "explanation" in q:
                    st.markdown(f'<div style="background-color:#fff3cd;padding:10px;border-radius:8px;color:#856404;">ℹ️ <b>Explanation:</b> {q["explanation"]}</div>', unsafe_allow_html=True)

                st.session_state.answered[q_index] = True

            if q_index < len(questions) - 1:
                if st.button("Next Question"):
                    st.session_state.quiz_index += 1
            else:
                st.markdown(f"""
                <div style="background-color:#e8f0fe;padding:20px;border-radius:10px;text-align:center;">
                    <h3 style="color:#0b5394;">🎉 Quiz Completed</h3>
                    <p style="font-size:18px;">Your Score: <b>{st.session_state.score} / {len(questions)}</b></p>
                </div>
                """, unsafe_allow_html=True)
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
        diff_text = "\n".join(diff_lines)  # ✅ FIXED

        if diff_text.strip():
            st.code(diff_text, language="diff")

            st.subheader("💬 Reviewer Comment")
            user_comment = st.text_area("Leave your feedback or observations below:", key="diff_comment", height=150)

            if st.button("💾 Save Comment"):
                comment_path = f"comments/comment_{lab_choice.lower().replace(' ', '_')}_{step_choice.lower().replace(' ', '_')}.txt"
                os.makedirs("comments", exist_ok=True)
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
            st.write("Score will appear after quiz interaction.")

# --- Page: Student Upload ---
elif page == "Student Upload":
    st.header("📤 Student Upload and View")
    st.markdown("Upload your lab solutions and view previously uploaded files.")

    lab = st.selectbox("Select Lab", ["Lab 1"])
    step = st.selectbox("Select Step", ["Step 1"])
    uploaded_file = st.file_uploader("Upload your solution (.txt, .py, .js, or .zip)", type=["txt", "py", "js", "zip"])

    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    if uploaded_file is not None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"student_{lab.replace(' ', '_')}_{step.replace(' ', '_')}_{timestamp}_{uploaded_file.name}"
        save_path = os.path.join(uploads_dir, filename)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())
        st.success(f"✅ File uploaded and saved as {filename}")

    st.subheader("📁 Previously Uploaded Files")
    uploaded_files = sorted(os.listdir(uploads_dir), reverse=True)
    for fname in uploaded_files:
        if fname.startswith("student_"):
            st.markdown(f"- {fname}")

# --- Page: Lecturer View ---
elif page == "Lecturer View":
    st.header("👨‍🏫 Lecturer View of Student Submissions")
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    student_files = sorted([f for f in os.listdir(uploads_dir) if f.startswith("student_")], reverse=True)

    selected_lab = st.selectbox("Filter by Lab", ["All"] + sorted(set([f.split("_")[1] for f in student_files])))
    filtered = student_files if selected_lab == "All" else [f for f in student_files if f"_{selected_lab}_" in f]

    for fname in filtered:
        st.markdown(f"📄 **{fname}**")
        with open(os.path.join(uploads_dir, fname), "r", encoding="utf-8", errors="ignore") as f:
            st.code(f.read(), language="javascript" if fname.endswith(".js") else "python")

    st.subheader("📤 Export Submissions to CSV")
    rows = []
    for fname in student_files:
        parts = fname.split("_")
        if len(parts) >= 4:
            lab = parts[1]
            step = parts[2]
            timestamp = parts[3]
            rows.append({
                "filename": fname,
                "lab": lab,
                "step": step,
                "timestamp": timestamp
            })
    df = pd.DataFrame(rows)
    if not df.empty:
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "student_submissions.csv", "text/csv")

    st.subheader("📝 Show Differences from Solution")
    if st.checkbox("Compare each submission with solution"):
        solution_path = os.path.join("data", "solution_lab_1_step_1.txt")
        try:
            with open(solution_path, "r", encoding="utf-8", errors="ignore") as solf:
                solution_lines = solf.readlines()

            for fname in filtered:
                student_path = os.path.join(uploads_dir, fname)
                try:
                    with open(student_path, "r", encoding="utf-8", errors="ignore") as studf:
                        student_lines = studf.readlines()
                    st.markdown(f"#### Diff: {fname}")
                    diff = difflib.HtmlDiff().make_table(solution_lines, student_lines,
                                                         fromdesc="Solution", todesc=fname,
                                                         context=True, numlines=3)
                    st.components.v1.html(diff, height=400, scrolling=True)
                except Exception as e:
                    st.error(f"Could not read {fname}: {e}")
        except FileNotFoundError:
            st.warning("Solution file not found for comparison.")