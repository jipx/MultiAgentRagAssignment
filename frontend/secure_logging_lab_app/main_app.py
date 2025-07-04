import streamlit as st
import os
import requests
import json
from utils import get_filename, poll_for_answer
from lab_tabs import render_lab_tabs

st.set_page_config(page_title="Secure Lab App", layout="wide")

# --- Constants ---
LAB_KEYS = ["labnotes", "quiz", "solution", "original"]

# --- Initialize uploaded files from 'data/' folder ---
def init_uploaded_from_data_folder():
    base_path = os.path.join(os.getcwd(), "data")
    uploaded = {}
    os.makedirs(base_path, exist_ok=True)

    for key in LAB_KEYS:
        uploaded[key] = next((os.path.join(base_path, f) for f in os.listdir(base_path) if f.startswith(key)), None)

    return uploaded

# --- Initialize session state ---
for var, default in {"uploaded": init_uploaded_from_data_folder(), "request_id": None, "user_id": ""}.items():
    if var not in st.session_state:
        st.session_state[var] = default

# --- Page title and selectors ---
st.title("🗕️ Secure Logging Lab")
col1, col2, _ = st.columns([1, 1, 2])
lab_choice = col1.selectbox("Select Lab", ["Lab5"], key="lab_select")
step_choice = col2.selectbox("Select Step", ["Step1", "Step2"], key="step_select")

# --- Sidebar: Upload Interface ---
st.sidebar.header("📄 Upload Lab Files")
for key in LAB_KEYS:
    uploaded_file = st.sidebar.file_uploader(f"{key.capitalize()} File", type=["txt", "json"], key=f"uploader_{key}")
    if uploaded_file:
        ext = "json" if key == "quiz" else "txt"
        file_path = get_filename(key, lab_choice, step_choice, ext)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        st.session_state.uploaded[key] = file_path
        st.sidebar.success(f"{key.capitalize()} uploaded and saved.")

# --- Sidebar: Display Loaded Files ---
st.sidebar.markdown("### 📂 Loaded Files")
for key, path in st.session_state.uploaded.items():
    icon = "✅" if path else "❌"
    st.sidebar.markdown(f"- {icon} **{key}**: `{path or 'Not Found'}`")

# --- Sidebar: User ID Input ---
st.sidebar.text_input("User ID", key="user_id_input", on_change=lambda: st.session_state.update({"user_id": st.session_state.user_id_input}))

# --- Sidebar: Generate Quiz Button ---
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

                    # --- Poll for answer using utility ---
                    result = poll_for_answer(
                        get_url,
                        st.session_state.request_id,
                        max_attempts=10,
                        delay_sec=3,
                        debug_sidebar=st.sidebar
                    )

                    raw_text = result.get("answer", [{}])[0].get("text", "")
                    json_text = raw_text[raw_text.find("{"):] if "{" in raw_text else raw_text

                    quiz_file = get_filename("quiz", lab_choice, step_choice, "json")
                    with open(quiz_file, "w", encoding="utf-8") as f:
                        f.write(json_text)
                    st.session_state.uploaded["quiz"] = quiz_file
                    st.success("✅ Quiz generated and saved.")

                    try:
                        quiz_data = json.loads(json_text)
                        st.subheader("🧠 Generated Quiz Questions")
                        for idx, q in enumerate(quiz_data.get("questions", []), 1):
                            with st.expander(f"Q{idx}: {q['question']}"):
                                st.markdown("**Choices:**")
                                for choice in q["choices"]:
                                    st.markdown(f"- {choice}")
                                st.markdown(f"**✅ Answer:** `{q['answer']}`")
                                st.markdown(f"**💡 Explanation:** {q['explanation']}")
                    except Exception as e:
                        st.error(f"⚠️ Failed to parse or display quiz: {e}")

        except Exception as e:
            st.error(f"❌ Error: {e}")

# --- Render Lab Interface ---
render_lab_tabs(lab_choice, step_choice, st.session_state.uploaded)
