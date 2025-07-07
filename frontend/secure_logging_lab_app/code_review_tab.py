import streamlit as st
import requests
from datetime import datetime
import json
import io
import pandas as pd
from utils import poll_for_answer, extract_codereview_feedback

ASK_URL = st.secrets["api"]["ask_url"]
GET_URL = st.secrets["api"]["get_answer_url"]

def render_code_review_tab():
    st.subheader("🔍 CodeReview Agent")

    user_id = st.text_input("👤 Student ID", value="student001", key="codereview_uid")

    examples = {
        "A01 - Unchecked Admin Role": """if (req.query.role === 'admin') {\n  grantAdminAccess();\n}""",
        "A02 - Plaintext Password": """app.post('/login', (req, res) => {\n  if (req.body.password === 'letmein') {\n    res.send('Welcome');\n  }\n});""",
        "A03 - SQL Injection": """app.get('/user/:id', (req, res) => {\n  const id = req.params.id;\n  db.query(`SELECT * FROM users WHERE id = ${id}`);\n});""",
        "A03 - Reflected XSS": """app.get('/search', (req, res) => {\n  const q = req.query.q;\n  res.send(`Results for ${q}`);\n});""",
        "A03 - XSS No Validation": """const userInput = req.body.comment;\nres.send(`<div>${userInput}</div>`);""",
        "A03 - XSS with Bad Regex": """const input = req.body.name;\nif (!/<script>/i.test(input)) {\n  res.send(input);\n}""",
        "A03 - Secure XSS Prevention (Whitelist)": """const input = req.body.name;\nif (/^[a-zA-Z0-9 ]+$/.test(input)) {\n  res.send(input);\n} else {\n  res.status(400).send('Invalid input');\n}""",
        "A04 - Missing Rate Limit": """app.post('/reset-password', (req, res) => {\n  resetPassword(req.body.email);\n});""",
        "A05 - Missing CSP Header": """app.use((req, res, next) => {\n  res.send('Hello');\n});""",
        "A06 - Outdated jQuery": """<script src="https://code.jquery.com/jquery-1.7.2.min.js"></script>""",
        "A07 - Insecure JWT Decode": """const decoded = jwt.decode(token);\nif (decoded.admin) { grantAccess(); }""",
        "A08 - Unsigned Update Script": """<script src="http://example.com/auto-update.js"></script>""",
        "A09 - No Logging on Login Fail": """if (!isValidPassword(user, pass)) {\n  res.send('Try again');\n}""",
        "A10 - Unrestricted URL Fetch": """app.get('/proxy', (req, res) => {\n  const url = req.query.url;\n  axios.get(url).then(resp => res.send(resp.data));\n});"""
    }

    selected_title = st.selectbox("📚 Choose a vulnerable code example", ["Select one..."] + list(examples.keys()), key="codereview_title")
    default_code = examples.get(selected_title, "")
    student_code = st.text_area("💻 Paste your code here", value=default_code, height=300, key="codereview_code")

    if st.button("Submit for Review", key="codereview_btn"):
        if not student_code.strip():
            st.warning("⚠️ Please enter or paste some code for review.")
            return

        payload = {
            "user_id": user_id,
            "topic": "codereview",
            "question": student_code
        }

        st.subheader("📤 Raw API Request Payload")
        st.json(payload)

        try:
            with st.spinner("Submitting for review..."):
                res = requests.post(ASK_URL, json=payload)
                ask_data = res.json()

            st.subheader("📥 Raw Ask API Response")
            st.json(ask_data)

            if res.status_code != 200:
                st.error(f"❌ Ask API error: {res.status_code}")
                return

            request_id = ask_data.get("message", {}).get("request_id")
            if not request_id:
                st.error("❌ Failed to get request ID from response.")
                return

            with st.spinner("🕒 Waiting for feedback..."):
                st.session_state.request_id = request_id
                answer = poll_for_answer(GET_URL, request_id, max_attempts=10, delay_sec=3, debug_sidebar=st.sidebar)

            st.subheader("📄 Raw Get Answer Response")
            st.json(answer)

            formatted_feedback = extract_codereview_feedback(answer)

            st.markdown("### 🔎 Review Feedback")
            st.markdown(formatted_feedback, unsafe_allow_html=True)

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
                st.markdown(entry["feedback"], unsafe_allow_html=True)
                st.markdown("---")

            # Download as JSON
            history_json = json.dumps(st.session_state.history, indent=2)
            st.download_button(
                label="📥 Download History as JSON",
                data=history_json,
                file_name=f"codereview_history_{user_id}.json",
                mime="application/json"
            )

            # Download as CSV
            df = pd.DataFrame(st.session_state.history)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📄 Download History as CSV",
                data=csv_buffer.getvalue(),
                file_name=f"codereview_history_{user_id}.csv",
                mime="text/csv"
            )

            if st.button("🗑️ Clear History"):
                st.session_state.history.clear()
                st.experimental_rerun()
        else:
            st.info("No review history yet.")
