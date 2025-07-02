import streamlit as st
import os
import requests
import json
import time
from utils import get_filename

def handle_upload_and_quiz_gen(lab_choice, step_choice):
    st.sidebar.markdown("### 📥 Upload Quiz & Generate")
    uploaded_quiz = st.sidebar.file_uploader("Upload Quiz", type="json", key="quiz_upload")

    if uploaded_quiz:
        save_path = get_filename("quiz", lab_choice, step_choice, "json")
        with open(save_path, "wb") as f:
            f.write(uploaded_quiz.read())
        st.session_state.uploaded["quiz"] = save_path
        st.sidebar.success("✅ Quiz uploaded and saved.")

    if st.sidebar.button("🧠 Generate Quiz from Lab Notes"):
        lab_file = st.session_state.uploaded.get("labnotes")
        if not lab_file or not os.path.exists(lab_file):
            st.sidebar.warning("⚠️ Please upload Lab Notes first to generate quiz.")
            return

        with open(lab_file, "r", encoding="utf-8") as f:
            lab_text = f.read()

        payload = {
            "question": lab_text,
            "topic": "sc-labquiz-gen",
            "sub_topic": f"{lab_choice.lower()}-{step_choice.lower()}",
            "user_id": st.session_state.get("user_id", "unknown")
        }

        try:
            ask_url = st.secrets["api"]["ask_url"]
            get_url = st.secrets["api"]["get_answer_url"]

            with st.sidebar.status("⏳ Generating quiz... Please wait", expanded=True) as status:
                with st.sidebar.expander("📤 Request Payload"):
                    st.code(json.dumps(payload, indent=2), language="json")

                res = requests.post(ask_url, json=payload)
                ask_data = res.json()

                with st.sidebar.expander("📥 Ask API Response"):
                    st.code(json.dumps(ask_data, indent=2), language="json")

                if res.status_code != 200 or "request_id" not in ask_data:
                    status.update(label="❌ Quiz request failed", state="error")
                    return

                request_id = ask_data["request_id"]
                st.session_state.request_id = request_id

                status.update(label="📡 Polling for quiz...", state="running")
                for i in range(10):
                    time.sleep(3)
                    get_res = requests.get(get_url, params={"request_id": request_id})
                    try:
                        result = get_res.json()
                    except Exception:
                        result = {"error": get_res.text}

                    with st.sidebar.expander(f"📥 Poll Attempt {i+1}"):
                        st.code(json.dumps(result, indent=2), language="json")

                    if "answer" in result:
                        quiz_file = get_filename("quiz", lab_choice, step_choice, "json")
                        with open(quiz_file, "w", encoding="utf-8") as f:
                            f.write(result["answer"])
                        st.session_state.uploaded["quiz"] = quiz_file
                        st.sidebar.success("✅ Quiz generated and saved.")
                        status.update(label="✅ Quiz ready!", state="complete")
                        break
                else:
                    st.sidebar.warning("⚠️ Timed out polling quiz.")
                    status.update(label="⚠️ Timed out", state="error")

        except Exception as e:
            st.sidebar.error(f"❌ Exception: {str(e)}")
