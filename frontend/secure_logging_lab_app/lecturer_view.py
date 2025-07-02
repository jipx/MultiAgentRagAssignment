import streamlit as st
import os

def get_filename(prefix, lab, step, ext):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
    os.makedirs(base_dir, exist_ok=True)
    filename = f"{prefix}_{lab.lower().replace(' ', '_')}_{step.lower().replace(' ', '_')}.{ext}"
    return os.path.join(base_dir, filename)

def render_lecturer_view(lab_choice, step_choice):
    st.header("🧑‍🏫 Lecturer View")

    code_path = get_filename("studentcode", lab_choice, step_choice, "txt")
    try:
        with open(code_path, encoding="utf-8", errors="ignore") as f:
            code = f.read()
        st.code(code, language="python")
    except FileNotFoundError:
        st.warning("No student code found for the selected lab and step.")

    comment_path = os.path.join(os.getcwd(), "comments", f"comment_{lab_choice}_{step_choice}.txt")
    if os.path.exists(comment_path):
        with open(comment_path, encoding="utf-8", errors="ignore") as f:
            comment = f.read()
        st.subheader("💬 Student Feedback")
        st.text_area("Comment", value=comment, height=150)
    else:
        st.info("No feedback available yet.")
