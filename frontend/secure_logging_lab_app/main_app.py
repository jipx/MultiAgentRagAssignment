import streamlit as st
import os
import requests
import time
import json
from utils import get_filename
from lab_tabs import render_lab_tabs



st.set_page_config(page_title="Secure Lab App", layout="wide")

# --- Initialize uploaded files from 'data/' folder ---
def init_uploaded_from_data_folder():
    base_path = "data"
    lab_keys = ["labnotes", "quiz", "solution", "original"]
    uploaded = {}
    for key in lab_keys:
        for filename in os.listdir(base_path):
            if filename.startswith(key):
                uploaded[key] = os.path.join(base_path, filename)
                break
        else:
            uploaded[key] = None
    return uploaded

if "uploaded" not in st.session_state:
    st.session_state.uploaded = init_uploaded_from_data_folder()

if "request_id" not in st.session_state:
    st.session_state.request_id = None

if "user_id" not in st.session_state:
    st.session_state.user_id = ""

# --- Lab + Step navigation ---
st.title("🔐 Secure Logging Lab")
col1, col2, col3 = st.columns([1, 1, 2])
lab_choice = col1.selectbox("Select Lab", ["Lab5"], key="lab_select")
step_choice = col2.selectbox("Select Step", ["Step1", "Step2"], key="step_select")

# --- Sidebar Upload Interface ---
st.sidebar.header("📤 Upload Lab Files")
lab_keys = ["labnotes", "quiz", "solution", "original"]
uploaded_files = {}

for key in lab_keys:
    uploaded_file = st.sidebar.file_uploader(f"{key.capitalize()} File", type=["txt", "json"], key=f"uploader_{key}")
    if uploaded_file:
        file_path = get_filename(key, lab_choice, step_choice, "txt" if key != "quiz" else "json")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        st.session_state.uploaded[key] = file_path
        st.sidebar.success(f"{key.capitalize()} uploaded and saved.")

# 🆕 Display loaded file paths for confirmation
st.sidebar.markdown("### 📂 Loaded Files")
for key, path in st.session_state.uploaded.items():
    if path:
        st.sidebar.markdown(f"- ✅ **{key}**: `{path}`")
    else:
        st.sidebar.markdown(f"- ❌ **{key}**: Not Found")

# --- User ID ---
st.sidebar.text_input("User ID", key="user_id_input", on_change=lambda: st.session_state.update({"user_id": st.session_state.user_id_input}))

# --- Generate Quiz ---
st.sidebar.markdown("---")
if st.sidebar.button("🧠 Generate Quiz"):
    lab_file = st.session_state.uploaded.get("labnotes")
    if not lab_file or not os.path.exists(lab_file):
        st.sidebar.warning("⚠️ Please upload Lab Notes first to generate quiz.")
    else:
        with open(lab_file, "r", encoding="utf-8") as f:
            lab_text = f.read()

        ask_payload = {
            "question": lab_text,
            "topic": "sc-labquiz-gen",
            "sub_topic": f"{lab_choice.lower()}-{step_choice.lower()}",
            "user_id": st.session_state.user_id or "unknown"
        }

        st.sidebar.markdown("**📤 Request Payload:**")
        st.sidebar.code(json.dumps(ask_payload, indent=2), language="json")

        try:
            ask_url = st.secrets["api"]["ask_url"]
            get_url = st.secrets["api"]["get_answer_url"]

            with st.spinner("⏳ Generating quiz..."):
                ask_response = requests.post(ask_url, json=ask_payload)
                ask_data = ask_response.json()
                st.session_state.request_id = ask_data.get("request_id")

                st.sidebar.markdown("**📥 Ask API Response:**")
                st.sidebar.code(json.dumps(ask_data, indent=2), language="json")

                if st.session_state.request_id:
                    poll_attempts = 10
                    for attempt in range(poll_attempts):
                        time.sleep(3)
                        get_resp = requests.get(get_url, params={"request_id": st.session_state.request_id})
                        result = get_resp.json()

                        st.sidebar.markdown(f"**📥 Poll Attempt {attempt + 1}:**")
                        st.sidebar.code(json.dumps(result, indent=2), language="json")

                        if "answer" in result:
                            quiz_file = get_filename("quiz", lab_choice, step_choice, "json")
                            with open(quiz_file, "w", encoding="utf-8") as f:
                                f.write(result["answer"])
                            st.session_state.uploaded["quiz"] = quiz_file
                            st.success("✅ Quiz generated and saved.")
                            break
                    else:
                        st.error("⚠️ Timed out waiting for quiz answer.")
                else:
                    st.error("❌ No request_id returned from Ask API.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# --- Render Lab Interface ---
render_lab_tabs(lab_choice, step_choice, st.session_state.uploaded)
