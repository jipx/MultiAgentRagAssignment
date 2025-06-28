import streamlit as st
import requests
import json
import time
import re
from datetime import datetime, timezone

# --- API and Secrets ---
ASK_URL = st.secrets["api"]["ask_url"]
GET_ANSWER_URL = st.secrets["api"]["get_answer_url"]
HISTORY_URL = st.secrets["api"]["history_url"]
DELETE_URL = st.secrets["api"]["delete_url"]
ADMIN_PASSCODE = st.secrets["api"]["admin_passcode"]

st.set_page_config(page_title="Assignment & OWASP Q&A", page_icon="📘")
st.title("📘 Assignment & OWASP Q&A System")

tab1, tab2, tab3 = st.tabs(["🔍 Ask a Question", "📜 View My History", "🛡️ Admin View"])

# --- TAB 1: Ask a Question ---
with tab1:
    user_id = st.text_input("👤 Student ID", value="student001", max_chars=10)
    question = st.text_area("📝 What is your question?", height=150)
    topic = st.selectbox("📚 Choose topic", ["assignment", "owasp", "assignment+owasp"])

    if st.session_state.get("followup_submitted"):
        question = st.session_state.get("followup_question", question)
        st.session_state.pop("followup_submitted", None)

    if st.session_state.get("followup_question") and not st.session_state.get("persisted_request_id"):
        st.session_state["auto_ask_followup"] = True

    ask_disabled = st.session_state.get("persisted_request_id") is not None
    if st.button("Ask", key="ask_button", disabled=ask_disabled) or \
       st.session_state.get("retry_requested") or \
       st.session_state.get("auto_ask_followup"):

        st.session_state.pop("auto_ask_followup", None)
        st.session_state["retry_requested"] = False

        if not question.strip():
            st.warning("Please enter a question.")
        else:
            payload = {
                "user_id": user_id,
                "question": question,
                "topic": topic,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            ask_status = None
            ask_data = {}
            raw_response = ""
            answer_text = None
            returned_request_id = None

            if not st.session_state.get("persisted_request_id"):
                try:
                    ask_response = requests.post(ASK_URL, json=payload)
                    ask_status = ask_response.status_code
                    ask_response.raise_for_status()
                    ask_json = ask_response.json()

                    ask_data = ask_json.get("message", {})
                    returned_request_id = ask_data.get("request_id")

                    if not returned_request_id:
                        raise ValueError("❌ No request_id found in 'message' field.")

                    st.session_state["persisted_request_id"] = returned_request_id

                except requests.exceptions.RequestException as e:
                    st.session_state.pop("persisted_request_id", None)
                    st.error(f"❌ API error: {e}")
                    with st.expander("📦 Debug Info"):
                        st.markdown(f"**Submit Status Code:** `{ask_status}`")
                        st.code(json.dumps(payload, indent=2), language="json")
                        st.code(ask_response.text if 'ask_response' in locals() else str(e), language="json")
                    st.stop()
            else:
                ask_data = {"request_id": st.session_state["persisted_request_id"]}
                ask_status = "retried"
                returned_request_id = st.session_state["persisted_request_id"]

            st.info("⏳ Waiting for the system to generate an answer...")
            max_retries = 10

            for attempt in range(1, max_retries + 1):
                with st.spinner(f"🔄 Attempt {attempt}/{max_retries}..."):
                    time.sleep(2 * attempt)
                    get_answer_url = f"{GET_ANSWER_URL}?request_id={returned_request_id}"
                    try:
                        answer_response = requests.get(get_answer_url)
                        answer_status = answer_response.status_code
                        answer_response.raise_for_status()
                        answer_data = answer_response.json()
                        answer_text = answer_data.get("answer", None)
                        raw_response = json.dumps(answer_data, indent=2)
                        if answer_text and answer_text != "_No answer returned._":
                            break
                    except Exception:
                        raw_response = answer_response.text
                        continue

            if answer_text:
                st.success("✅ Answer")
                st.markdown(answer_text)
                st.session_state.pop("persisted_request_id", None)

                def extract_follow_ups(answer):
                    match = re.search(r'{\s*"follow_up"\s*:\s*\[.*?\]\s*}', answer, re.DOTALL)
                    if match:
                        try:
                            return json.loads(match.group(0)).get("follow_up", [])
                        except:
                            return []
                    return []

                followup_options = extract_follow_ups(answer_text)
                if followup_options:
                    st.subheader("🔁 Follow-up Suggestions")
                    selected_followup = st.radio("Choose a follow-up to ask:", followup_options, key="followup_choice")

                    if st.button("🎯 Ask Follow-up Question"):
                        st.session_state["followup_question"] = selected_followup
                        st.session_state["followup_submitted"] = True
                        st.session_state.pop("persisted_request_id", None)
                        st.session_state["auto_ask_followup"] = True
                        st.rerun()

            else:
                st.warning("⚠️ No answer returned after multiple attempts.")
                if st.button("🔁 Retry to Get Answer", key="retry_button"):
                    st.session_state["retry_requested"] = True
                    st.experimental_rerun()

            with st.expander("📦 View Request and Response"):
                st.markdown(f"**Submit Status Code:** `{ask_status}`")
                st.markdown(f"**Answer Status Code:** `{answer_status}`")
                st.markdown(f"**Used request_id:** `{returned_request_id}`")
                st.code(json.dumps(payload, indent=2), language="json")
                st.code(json.dumps(ask_data, indent=2), language="json")
                st.code(raw_response, language="json")