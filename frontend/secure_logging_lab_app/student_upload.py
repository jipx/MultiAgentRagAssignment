import streamlit as st
import os

def get_filename(prefix, lab, step, ext):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
    os.makedirs(base_dir, exist_ok=True)
    filename = f"{prefix}_{lab.lower().replace(' ', '_')}_{step.lower().replace(' ', '_')}.{ext}"
    return os.path.join(base_dir, filename)

def render_student_upload(lab_choice, step_choice):
    st.header("📤 Student Uploads")

    code_input = st.text_area("Paste your code here", height=300)

    if st.button("Save My Code"):
        save_path = get_filename("studentcode", lab_choice, step_choice, "txt")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(code_input)
        st.success(f"✅ Code saved to {save_path}")
