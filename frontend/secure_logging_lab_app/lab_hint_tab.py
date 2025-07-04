import streamlit as st
import requests
from utils import poll_for_answer

ASK_URL = st.secrets["api"]["ask_url"]

def render_lab_hint_tab():
    st.subheader("🧠 LabHint Agent")

    user_id = st.text_input("👤 Student ID", value="student001", key="labhint_uid")
    lab_notes = st.text_area("📘 Lab Notes", height=200, key="labhint_notes")
    student_question = st.text_input("❓ What’s your question?", key="labhint_q")

    if st.button("Ask for Hint", key="labhint_btn"):
        payload = {
            "user_id": user_id,
            "topic": "labhint",
            "lab_notes": lab_notes,
            "student_question": student_question
        }
        res = requests.post(ASK_URL, json=payload)
        request_id = res.json().get("request_id")

        if request_id:
            answer = poll_for_answer(request_id)
            st.markdown(f"**💡 Hint:**\n\n{answer}")
        else:
            st.error("❌ Failed to get a response.")
