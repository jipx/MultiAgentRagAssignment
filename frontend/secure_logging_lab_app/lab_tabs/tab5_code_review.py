import streamlit as st
import requests
from utils import poll_for_answer

ASK_URL = st.secrets["api"]["ask_url"]

def render_tab(uploaded):
    st.subheader("🔍 CodeReview Agent")

    user_id = st.text_input("👤 Student ID", value="student001", key="codereview_uid")
    student_code = st.text_area("💻 Paste your code here", height=300, key="codereview_code")

    if st.button("Submit for Review", key="codereview_btn"):
        payload = {
            "user_id": user_id,
            "topic": "codereview",
            "student_question_with_code": student_code
        }
        res = requests.post(ASK_URL, json=payload)
        request_id = res.json().get("request_id")

        if request_id:
            answer = poll_for_answer(request_id)
            st.markdown(f"**🔎 Review Feedback:**\n\n{answer}")
        else:
            st.error("❌ Failed to get a response.")
