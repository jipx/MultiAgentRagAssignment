import streamlit as st
import os
import difflib
import json
from pathlib import Path
from lab_hint_tab import render_lab_hint_tab
from code_review_tab import render_code_review_tab

def get_filename(prefix, lab, step, ext):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
    os.makedirs(base_dir, exist_ok=True)
    filename = f"{prefix}_{lab.lower().replace(' ', '_')}_{step.lower().replace(' ', '_')}.{ext}"
    return os.path.join(base_dir, filename)

def load_file_content(file_input, default_text):
    try:
        if file_input and hasattr(file_input, "read"):
            return file_input.read().decode("utf-8", errors="ignore")
        if isinstance(file_input, str) or isinstance(file_input, Path):
            with open(file_input, encoding="utf-8", errors="ignore") as f:
                return f.read()
        return default_text
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return default_text

def load_quiz_data(file_input):
    try:
        if file_input and hasattr(file_input, "read"):
            return json.load(file_input)
        if isinstance(file_input, str) or isinstance(file_input, Path):
            with open(file_input, encoding="utf-8", errors="ignore") as f:
                return json.load(f)
        return {"questions": []}
    except Exception as e:
        st.error(f"Failed to load quiz data: {e}")
        return {"questions": []}

def save_quiz_to_data_folder(quiz_data, lab, step):
    try:
        filename = get_filename("quiz", lab, step, "json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)
        st.success(f"✅ Quiz saved to: `{filename}`")
        return filename
    except Exception as e:
        st.error(f"❌ Could not save quiz: {e}")
        return None

def get_uploaded_or_default(key, lab, step):
    lab_step_key = f"{lab.lower()}_{step.lower()}"
    uploaded_group = st.session_state.uploaded.get(lab_step_key, {})
    ext = "json" if key == "quiz" else "txt"
    return uploaded_group.get(key) or get_filename(key, lab, step, ext)

def render_lab_tabs(lab_choice, step_choice, uploaded=None):
    if "uploaded" not in st.session_state:
        st.session_state.uploaded = uploaded or {}

    tabs = st.tabs(["Lab", "Hint", "Quiz", "Solution", "Lab Score", "Code Review"])
    lab_step_key = f"{lab_choice.lower()}_{step_choice.lower()}"
    uploaded_group = st.session_state.uploaded.get(lab_step_key, {})

    with tabs[0]:
        st.header("🧪 Lab Content")
        lab_file = get_uploaded_or_default("labnotes", lab_choice, step_choice)
        lab_notes = load_file_content(lab_file, "⚠️ Lab notes not found.")
        st.session_state.labnotes = lab_notes

        if lab_notes:
            with st.expander("📄 View Full Lab Notes", expanded=True):
                st.markdown(lab_notes)
            st.download_button(
                label="⬇️ Download Lab Notes",
                data=lab_notes,
                file_name=os.path.basename(lab_file),
                mime="text/plain"
            )
        else:
            st.info("No lab notes available.")

    with tabs[1]:
        st.header("Lab Hint")
        render_lab_hint_tab(lab_choice, step_choice)

    with tabs[2]:
        st.header("🧠 Quiz")
        quiz_file = get_uploaded_or_default("quiz", lab_choice, step_choice)
        quiz_data = load_quiz_data(quiz_file)
        questions = quiz_data.get("questions", [])

        if uploaded_group.get("quiz") and questions:
            save_quiz_to_data_folder(quiz_data, lab_choice, step_choice)

        if questions:
            if "submitted_answers" not in st.session_state:
                st.session_state.submitted_answers = {}

            st.write(f"Total Questions: {len(questions)}")

            for idx, q in enumerate(questions):
                st.markdown(f"**Q{idx+1}: {q['question']}**")
                key_suffix = f"{lab_choice}_{step_choice}_{idx}".replace(" ", "_").lower()
                selected = st.radio(
                    f"Choices for Q{idx+1}",
                    q.get("choices", []),
                    key=f"q_{key_suffix}"
                )
                st.session_state.submitted_answers[idx] = selected
                st.markdown("---")

            if st.button("Submit All"):
                score = 0
                for idx, q in enumerate(questions):
                    correct = q.get("answer", "").strip().lower()
                    submitted = st.session_state.submitted_answers.get(idx, "").strip().lower()
                    if submitted == correct:
                        st.success(f"✅ Q{idx+1} Correct")
                        score += 1
                    else:
                        st.error(f"❌ Q{idx+1} Incorrect (Correct: {q['answer']})")
                        if "explanation" in q:
                            st.info(f"ℹ️ Explanation: {q['explanation']}")
                st.subheader(f"🎉 Total Score: {score} / {len(questions)}")
        else:
            st.info("No quiz questions found.")

    with tabs[3]:
        st.header("🔍 Code Difference (Unified View)")
        solution_file = get_uploaded_or_default("solution", lab_choice, step_choice)
        original_file = get_uploaded_or_default("original", lab_choice, step_choice)

        solution_content = load_file_content(solution_file, "Solution not available.")
        original_content = load_file_content(original_file, "Original code not available.")
        solution = solution_content.splitlines()
        original = original_content.splitlines()

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
                comments_dir = os.path.join(os.getcwd(), "comments")
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
        if "submitted_answers" in st.session_state:
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

    with tabs[5]:
        render_code_review_tab()
