import streamlit as st
import difflib
import os
from utils import get_filename

def load_file_content(path, fallback_msg="File not found."):
    if not path or not os.path.exists(path):
        return fallback_msg
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def render_tab(uploaded):
    st.header("🔍 Code Difference (Unified View)")

    lab_choice = st.session_state.get("lab_choice", "Lab5")
    step_choice = st.session_state.get("step_choice", "Step1")

    solution_file = uploaded.get("solution") or get_filename("solution", lab_choice, step_choice, "txt")
    original_file = uploaded.get("original") or get_filename("original", lab_choice, step_choice, "txt")

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
