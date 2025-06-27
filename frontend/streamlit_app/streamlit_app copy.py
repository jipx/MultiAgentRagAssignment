import streamlit as st
import requests
import json
import time
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

    ask_disabled = st.session_state.get("persisted_request_id") is not None
    if st.button("Ask", key="ask_button", disabled=ask_disabled) or st.session_state.get("retry_requested"):
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

                    # ✅ Extract `request_id` from nested message
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


# --- TAB 2: View My History ---
with tab2:
    st.subheader("📜 Your Q&A History")
    hist_user_id = st.text_input("Enter your Student ID", value="student001")
    if st.button("Fetch My History"):
        try:
            hist_response = requests.get(HISTORY_URL)
            hist_response.raise_for_status()
            history_data = hist_response.json()
            user_history = [q for q in history_data if q.get("user_id") == hist_user_id]

            if not user_history:
                st.info("No questions found.")
            else:
                for i, record in enumerate(user_history, 1):
                    with st.expander(f"📝 Q{i}: {record.get('question')[:50]}..."):
                        st.markdown(f"**Topic:** {record.get('topic')}")
                        st.markdown(f"**Question:** {record.get('question')}")
                        st.markdown(f"**Answer:** {record.get('answer') or '_No answer yet_'}")
                        st.markdown(f"**Time:** `{record.get('timestamp', 'N/A')}`")
                        st.markdown(f"**Request ID:** `{record.get('request_id', 'N/A')}`")
        except Exception as e:
            st.error(f"⚠️ Could not fetch history: {e}")


# --- TAB 3: Admin View ---
with tab3:
    st.subheader("🛡️ Admin Q&A Viewer")
    admin_pass = st.text_input("Enter Admin Passcode", type="password")
    if st.button("View All Q&A History"):
        if admin_pass != ADMIN_PASSCODE:
            st.error("🚫 Invalid admin passcode.")
        else:
            try:
                response = requests.get(HISTORY_URL)
                response.raise_for_status()
                all_data = response.json()

                with st.expander("🔍 Filter Q&A Records"):
                    filter_user = st.text_input("Filter by Student ID (optional)")
                    filter_topic = st.selectbox("Filter by Topic", ["all", "assignment", "owasp", "assignment+owasp"])
                    limit_count = st.slider("Limit records", 1, 100, 30)

                filtered = all_data
                if filter_user:
                    filtered = [q for q in filtered if q.get("user_id") == filter_user]
                if filter_topic != "all":
                    filtered = [q for q in filtered if q.get("topic") == filter_topic]

                st.success(f"✅ Showing {min(len(filtered), limit_count)} of {len(filtered)} records")
                for i, q in enumerate(filtered[:limit_count], 1):
                    with st.expander(f"📄 Record {i} — {q.get('user_id')}"):
                        st.markdown(f"**Topic:** {q.get('topic')}")
                        st.markdown(f"**Question:** {q.get('question')}")
                        st.markdown(f"**Answer:** {q.get('answer') or '_No answer yet_'}")
                        st.markdown(f"**Time:** `{q.get('timestamp', 'N/A')}`")
                        st.markdown(f"**Request ID:** `{q.get('request_id', 'N/A')}`")

                        if st.button(f"🗑️ Delete Answer", key=f"delete_{i}"):
                            try:
                                del_url = f"{DELETE_URL}?request_id={q.get('request_id')}"
                                del_response = requests.delete(del_url)
                                del_response.raise_for_status()
                                st.success("✅ Deleted successfully. Please refresh.")
                            except Exception as e:
                                st.error(f"❌ Failed to delete: {e}")
            except Exception as e:
                st.error(f"⚠️ Failed to retrieve history: {e}")
