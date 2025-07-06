import streamlit as st
import requests
from datetime import datetime
from utils import poll_for_answer
from utils import extract_codereview_feedback

ASK_URL = st.secrets["api"]["ask_url"]
GET_URL = st.secrets["api"]["get_answer_url"]


def render_code_review_tab():
    st.subheader("🔍 CodeReview Agent")

    user_id = st.text_input("👤 Student ID", value="student001", key="codereview_uid")
    selected_title = st.selectbox("📚 Choose a code scenario", [
        "Select one...",
        "1. Basic SQL Injection (A03)",
        "2. Insecure JWT Verification (A07)",
        "3. Missing HTTPS Headers (A05)",
        "4. SSRF via URL Fetch (A10)"
    ], key="codereview_title")

    examples = {
        "1. Basic SQL Injection (A03)": "app.get('/user/:id', (req, res) => {\n  const userId = req.params.id;\n  db.query(`SELECT * FROM users WHERE id = ${userId}`);\n});",
        "2. Insecure JWT Verification (A07)": "const decoded = jwt.decode(token);\nif (decoded.role === 'admin') {\n  grantAccess();\n}",
        "3. Missing HTTPS Headers (A05)": "res.send('Welcome');",
        "4. SSRF via URL Fetch (A10)": "app.get('/proxy', (req, res) => {\n  const target = req.query.url;\n  axios.get(target).then(r => res.send(r.data));\n});"
    }

    default_code = examples.get(selected_title, "")
    student_code = st.text_area("💻 Paste your code here", value=default_code, height=300, key="codereview_code")

    if st.button("Submit for Review", key="codereview_btn"):
        payload = {
            "user_id": user_id,
            "topic": "codereview",
            "question": student_code
        }

        st.subheader("📤 Raw API Request Payload")
        st.json(payload)

        try:
            res = requests.post(ASK_URL, json=payload)
            ask_data = res.json()
            st.subheader("📥 Raw API Response")
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
                max_attempts=10,
                delay_sec=3,
                debug_sidebar=st.sidebar
            )

          
            # Show full raw JSON from the answer API
            st.subheader("📄 Raw Get Answer Response")
            st.json(answer)

            # Assume `answer_raw` is the .json()['answer'] value from API response (as a string)
            formatted_feedback = extract_codereview_feedback(answer)
            st.markdown("### 🔎 Review Feedback")
            st.markdown(formatted_feedback)

            # Save history
            if "history" not in st.session_state:
                st.session_state.history = []

            st.session_state.history.append({
                "title": selected_title,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "code": student_code,
                "feedback": formatted_feedback
            })

        except Exception as e:
            st.error(f"❌ Exception occurred: {str(e)}")

    with st.expander("🗂️ Review History", expanded=False):
        if "history" in st.session_state and st.session_state.history:
            for entry in reversed(st.session_state.history):
                st.markdown(f"### 📌 {entry['title']} — {entry['timestamp']}")
                st.code(entry["code"], language="javascript")
                st.markdown(f"**🔎 Feedback:**\n\n{entry['feedback']}")
                st.markdown("---")
            if st.button("🗑️ Clear History"):
                st.session_state.history.clear()
                st.experimental_rerun()
        else:
            st.info("No review history yet.")
