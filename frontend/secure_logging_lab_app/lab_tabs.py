import streamlit as st
import os
import difflib
import json

def get_filename(prefix, lab, step, ext):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
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

def render_lab_tabs(lab_choice, step_choice, uploaded=None):
    tabs = st.tabs(["Lab", "Hint", "Quiz", "Solution", "Lab Score"])

    with tabs[0]:
        st.header("Lab Content")
        lab_file = uploaded.get("labnotes") if uploaded else get_filename("labnotes", lab_choice, step_choice, "txt")
        lab_notes = load_file_content(lab_file, "Lab notes not found.")
        st.markdown(lab_notes)

    with tabs[1]:
        st.header("Hint")
        st.write(f"Hints for **{lab_choice} - {step_choice}**")
        st.text_area("Hint Details", height=150)

    with tabs[2]:
        st.header("🧠 Quiz")
        quiz_file = uploaded.get("quiz") if uploaded else get_filename("quiz", lab_choice, step_choice, "json")
        quiz_data = load_quiz_data(quiz_file)
        questions = quiz_data.get("questions", [])

        if questions:
            if 'submitted_answers' not in st.session_state:
                st.session_state.submitted_answers = {}

            st.write(f"Total Questions: {len(questions)}")

            for idx, q in enumerate(questions):
                st.markdown(f"**Q{idx+1}: {q['question']}**")
                selected = st.radio(
                    f"Choices for Q{idx+1}",
                    q.get("choices", []),
                    key=f"q_{idx}"
                )
                st.session_state.submitted_answers[idx] = selected
                st.markdown("---")

            if st.button("Submit All"):
                score = 0
                for idx, q in enumerate(questions):
                    correct = q.get("answer", "").strip().lower()
                    submitted = st.session_state.submitted_answers.get(idx, "").strip().lower()
                    if submitted == correct:
                        score += 1
                        st.success(f"✅ Q{idx+1} Correct")
                    else:
                        st.error(f"❌ Q{idx+1} Incorrect (Correct: {q['answer']})")
                        if "explanation" in q:
                            st.info(f"ℹ️ Explanation: {q['explanation']}")
                st.subheader(f"🎉 Total Score: {score} / {len(questions)}")
        else:
            st.info("No quiz questions found.")

    with tabs[3]:
        st.header("🔍 Code Difference (Unified View)")

        solution_file = uploaded.get("solution") if uploaded else get_filename("solution", lab_choice, step_choice, "txt")
        original_file = uploaded.get("original") if uploaded else get_filename("original", lab_choice, step_choice, "txt")
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
        if 'submitted_answers' in st.session_state:
            total = len(st.session_state.submitted_answers)
            correct = sum(
                1 for idx, q in enumerate(questions)
                if st.session_state.submitted_answers.get(idx, "").strip().lower()
                == q.get("answer", "").strip().lower()
            )
            st.metric(label="Questions Answered", value=total)
            st.metric(label="Correct Answers", value=f"{correct} / {total}")
        else:
            st.info("Score will appear after quiz interaction.")
