
import streamlit as st
import os
import json
import requests
from utils import get_filename, poll_for_answer
from lab_tabs import render_lab_tabs

# -------------------------------
# App Configuration
# -------------------------------
st.set_page_config(page_title="Secure Logging Lab", layout="wide")
st.title("🔐 Secure Coding: Lab-Based Adaptive Learning")

LAB_KEYS = ["labnotes", "quiz", "solution", "original"]

# -------------------------------
# Lab and Step Selection Defaults
# -------------------------------
if "lab_choice" not in st.session_state:
    st.session_state.lab_choice = "Lab5"
if "step_choice" not in st.session_state:
    st.session_state.step_choice = "Step1"

# -------------------------------
# Lab and Step Selection UI
# -------------------------------
col1, col2, _ = st.columns([1, 1, 2])
lab_choice = col1.selectbox("Select Lab", ["Lab5", "Lab6", "Lab7"], key="lab_choice")
step_choice = col2.selectbox("Select Step", ["Step1", "Step2", "Step3"], key="step_choice")

# -------------------------------
# Load files from data/ on startup
# -------------------------------
def init_uploaded_from_data_folder():
    base_path = os.path.join(os.getcwd(), "data")
    uploaded = {}
    os.makedirs(base_path, exist_ok=True)
    for key in LAB_KEYS:
        matching_file = next(
            (
                os.path.join(base_path, f)
                for f in os.listdir(base_path)
                if f.startswith(f"{key}_{st.session_state.lab_choice.lower()}_{st.session_state.step_choice.lower()}")
            ),
            None
        )
        uploaded[key] = matching_file
    return uploaded

for var, default in {
    "uploaded": init_uploaded_from_data_folder(),
    "request_id": None,
    "user_id": "",
}.items():
    if var not in st.session_state:
        st.session_state[var] = default

# -------------------------------
# Sidebar: User Type & Login
# -------------------------------
st.sidebar.header("👤 User")

user_type = st.sidebar.radio("User Type", ["Student", "Lecturer"], key="user_type")

if user_type == "Lecturer":
    lecturer_pwd = st.sidebar.text_input("Lecturer Password", type="password", key="lecturer_pwd")
    st.session_state["lecturer_authenticated"] = (lecturer_pwd == st.secrets["auth"]["lecturer_pwd"])
else:
    st.session_state["lecturer_authenticated"] = False

st.session_state["user_id"] = st.sidebar.text_input("User ID", key="user_id_input", value="p1234567").strip()

# -------------------------------
# Sidebar: Upload & Quiz (Lecturer Only)
# -------------------------------
if user_type == "Lecturer" and st.session_state["lecturer_authenticated"]:
    st.sidebar.header("📄 Upload Lab Files")
    for key in LAB_KEYS:
        uploaded_file = st.sidebar.file_uploader(f"{key.capitalize()} File", type=["txt", "json", "md"], key=f"uploader_{key}")
        if uploaded_file:
            ext = "json" if key == "quiz" else "txt"
            file_path = get_filename(key, lab_choice, step_choice, ext)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            st.session_state.uploaded[key] = file_path
            st.sidebar.success(f"{key.capitalize()} uploaded and saved to `data/`.")

    # Show Upload Status
    st.sidebar.markdown("### 📂 Loaded Files")
    for key in LAB_KEYS:
        path = st.session_state.uploaded.get(key)
        icon = "✅" if path and os.path.exists(path) else "❌"
        st.sidebar.markdown(f"- {icon} **{key}**: `{path or 'Not Found'}`")

    # Quiz Generation
    st.sidebar.markdown("---")
    if st.sidebar.button("🧠 Generate Quiz"):
        lab_file = st.session_state.uploaded.get("labnotes")
        if not lab_file or not os.path.exists(lab_file):
            st.sidebar.warning("⚠️ Please upload Lab Notes first to generate quiz.")
        else:
            with open(lab_file, encoding="utf-8") as f:
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
                    if ask_response.status_code != 200:
                        st.error(f"❌ Ask API error: {ask_response.status_code}")
                    else:
                        ask_data = ask_response.json()
                        st.session_state.request_id = ask_data.get("message", {}).get("request_id")

                        st.sidebar.markdown("**📥 Ask API Response:**")
                        st.sidebar.code(json.dumps(ask_data, indent=2), language="json")

                        result = poll_for_answer(
                            get_url,
                            st.session_state.request_id,
                            max_attempts=10,
                            delay_sec=3,
                            debug_sidebar=st.sidebar
                        )

                        try:
                            raw_body = result.get("answer", {}).get("body", "{}")
                            parsed_body = json.loads(raw_body)
                            quiz_data = parsed_body.get("questions", [])

                            quiz_file = get_filename("quiz", lab_choice, step_choice, "json")
                            with open(quiz_file, "w", encoding="utf-8") as f:
                                f.write(json.dumps({"questions": quiz_data}, indent=2))
                            st.session_state.uploaded["quiz"] = quiz_file
                            st.success("✅ Quiz generated and saved.")

                            st.subheader("🧠 Generated Quiz Questions")
                            with st.expander("📋 All Quiz Questions", expanded=False):
                                for idx, q in enumerate(quiz_data, 1):
                                    st.markdown("**Choices:**")
                                    for choice in q["choices"]:
                                        st.markdown(f"- {choice}")
                                    st.markdown(f"**✅ Answer:** `{q['answer']}`")
                                    st.markdown(f"**💡 Explanation:** {q['explanation']}")
                        except Exception as e:
                            st.error(f"⚠️ Failed to parse or display quiz: {e}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# -------------------------------
# Main Lab UI Tabs
# -------------------------------
render_lab_tabs(lab_choice, step_choice, st.session_state.uploaded)
