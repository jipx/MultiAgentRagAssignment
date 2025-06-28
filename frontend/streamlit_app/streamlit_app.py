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
    
    # --- Top inputs ---
    user_id = st.text_input("👤 Student ID", value="student001", max_chars=10)
    topic = st.selectbox("📚 Choose a topic", ["assignment", "owasp", "assignment+owasp"])

    # --- Init session state ---
    if "conversation" not in st.session_state:
        st.session_state["conversation"] = []
    if "ask_now" not in st.session_state:
        st.session_state["ask_now"] = False
    if "followup_question" not in st.session_state:
        st.session_state["followup_question"] = ""
    if "is_loading" not in st.session_state:
        st.session_state["is_loading"] = False

    # --- Always show follow-up input at the bottom ---
    st.markdown("### 💬 Ask a Question or Follow-up")
    followup_input = st.text_input("Type your question here:", key="manual_followup_input",max_chars=1000)

    ask_clicked = st.button("Ask", disabled=st.session_state["is_loading"])

    if ask_clicked:
        if not followup_input.strip():
            st.warning("Please enter a question.")
        else:
            st.session_state["followup_question"] = followup_input.strip()
            st.session_state["ask_now"] = True
            st.session_state["is_loading"] = True  # 🔒 lock Ask button
            st.rerun()

    # --- Trigger Ask logic if ask_now is True ---
    if st.session_state.get("ask_now"):
        st.session_state["ask_now"] = False
        question = st.session_state["followup_question"]
        st.session_state.pop("followup_question", None)

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
            st.session_state["is_loading"] = False  # 🔓 unlock Ask button
            st.error(f"❌ API error: {e}")
            st.stop()

        # --- Wait for answer with spinner ---
        with st.spinner("⏳ Generating answer, please wait..."):
            max_retries = 10
            for attempt in range(1, max_retries + 1):
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
            st.session_state.pop("persisted_request_id", None)
            st.session_state["conversation"].append({
                "question": question,
                "answer": answer_text
            })
            st.session_state["is_loading"] = False  # 🔓 unlock Ask button

    # --- Show latest Q&A and follow-ups ---
    if st.session_state.get("conversation"):
        latest = st.session_state["conversation"][-1]
        st.markdown("## ✅ Latest Answer")
        st.markdown(f"**Q:** {latest['question']}")
        st.markdown(f"**A:** {latest['answer']}")

        def extract_follow_ups(answer):
            match = re.search(r'{\s*"follow_up"\s*:\s*\[.*?\]\s*}', answer, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0)).get("follow_up", [])
                except:
                    return []
            return []

        followups = extract_follow_ups(latest["answer"])
        if followups:
            st.markdown("### 🔁 Suggested Follow-up Questions:")
            for fup in followups:
                st.markdown(f"- {fup}")

with tab2:
    st.markdown("## 📜 My Question & Answer History")

    st.markdown("Enter your student ID to view your past questions and answers.")
    history_user_id = st.text_input("👤 Student ID", value="student001", key="history_user_id")

    if st.button("🔍 Load History"):
        with st.spinner("Fetching your history..."):
            try:
                response = requests.get(f"{HISTORY_URL}?user_id={history_user_id}")
                response.raise_for_status()
                history_data = response.json()
                history_list = history_data.get("history", [])

                if not history_list:
                    st.info("📭 No Q&A history found for this student ID.")
                else:
                    st.success(f"✅ Found {len(history_list)} entries.")
                    st.markdown("---")

                    for idx, item in enumerate(reversed(history_list), 1):
                        question = item.get("question", "No question provided.")
                        answer = item.get("answer", "No answer available.")
                        timestamp = item.get("timestamp", "No timestamp")

                        # Format timestamp nicely
                        try:
                            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                            timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                        except Exception:
                            timestamp_str = timestamp

                        with st.expander(f"🔹 Q{idx}: {question[:80]}{'...' if len(question) > 80 else ''}"):
                            st.markdown(f"**🕒 Asked on:** `{timestamp_str}`")
                            st.markdown(f"**❓ Question:** {question}")
                            st.markdown("---")
                            st.markdown(f"**💡 Answer:**\n\n{answer}")

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Could not load history: {e}")

with tab3:
    st.markdown("## 🛡️ Admin View - All Q&A Records")
    admin_input = st.text_input("🔐 Enter admin passcode", type="password")
    show_all = st.button("📂 Load All Q&A")

    if show_all:
        if admin_input != ADMIN_PASSCODE:
            st.error("❌ Invalid passcode.")
        else:
            with st.spinner("Loading all Q&A history..."):
                try:
                    response = requests.get(f"{HISTORY_URL}?user_id=all")
                    response.raise_for_status()
                    data = response.json()
                    all_records = data.get("history", data)  # fallback for list-style response

                    if not all_records:
                        st.info("📭 No records found.")
                    else:
                        st.success(f"✅ Loaded {len(all_records)} records.")
                        st.markdown("---")

                        for idx, item in enumerate(reversed(all_records), 1):
                            user = item.get("user_id", "N/A")
                            question = item.get("question", "N/A")
                            answer = item.get("answer", "N/A")
                            timestamp = item.get("timestamp", "N/A")

                            try:
                                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                                timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                            except:
                                timestamp_str = timestamp

                            with st.expander(f"🧾 Entry {idx} | 👤 {user} | 🕒 {timestamp_str}"):
                                st.markdown(f"**❓ Question:** {question}")
                                st.markdown("---")
                                st.markdown(f"**💡 Answer:**\n\n{answer}")

                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Failed to fetch data: {e}")
