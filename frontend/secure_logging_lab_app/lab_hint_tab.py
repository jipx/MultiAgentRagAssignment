import streamlit as st
import requests
from datetime import datetime
from utils import poll_for_answer

ASK_URL = st.secrets["api"]["ask_url"]
GET_URL = st.secrets["api"]["get_answer_url"]

def render_lab_hint_tab():
    st.subheader("💡 LabHints Agent")

    user_id = st.text_input("👤 Student ID", value="student001", key="labhint_uid")
    task_question = st.text_area("❓ Enter your task or question", height=150, key="labhint_question")

    labnotes = st.session_state.get("labnotes", "")

    if st.button("Submit for Hint", key="labhint_submit"):
        # Construct full question with lab context
        full_question = f"Task: {task_question}\nContext:\n{labnotes}"

        payload = {
            "user_id": user_id,
            "topic": "labhint",
            "question": full_question
        }

        st.subheader("📤 Raw API Request Payload")
        st.json(payload)

        try:
            res = requests.post(ASK_URL, json=payload)

            st.subheader("📥 Raw Ask API Response (text)")
            st.code(res.text, language="json")

            ask_data = res.json()
            st.subheader("📥 Parsed Ask API Response (JSON)")
            st.json(ask_data)

            if res.status_code != 200:
                st.error(f"❌ Ask API error: {res.status_code}")
                return

            request_id = ask_data.get("message", {}).get("request_id")
            if not request_id:
                st.error("❌ Failed to get request ID from response.")
                return

            st.session_state.request_id = request_id
            answer = poll_for_answer(
                GET_URL,
                request_id,
                max_attempts=15,
                delay_sec=3,
                debug_sidebar=st.sidebar
            )

            st.subheader("🔎 Hint")
            st.markdown(answer, unsafe_allow_html=True)

            if "labhint_history" not in st.session_state:
                st.session_state.labhint_history = []

            st.session_state.labhint_history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "task": task_question,
                "notes": labnotes,
                "hint": answer
            })

        except Exception as e:
            st.error(f"❌ Exception occurred: {str(e)}")

    with st.expander("📚 Hint History", expanded=False):
        if "labhint_history" in st.session_state and st.session_state.labhint_history:
            for entry in reversed(st.session_state.labhint_history):
                st.markdown(f"### 🕒 {entry['timestamp']}")
                st.markdown(f"**Task:** {entry['task']}")
                if entry["notes"]:
                    st.markdown(f"**Context:**\n```text\n{entry['notes']}\n```")
                st.markdown("**Hint:**")
                st.markdown(entry["hint"], unsafe_allow_html=True)
                st.markdown("---")
            if st.button("🗑️ Clear Hint History"):
                st.session_state.labhint_history.clear()
                st.experimental_rerun()
        else:
            st.info("No hints yet.")
