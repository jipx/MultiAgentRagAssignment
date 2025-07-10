import json
import requests
import streamlit as st
from datetime import datetime
from collections import defaultdict
from utils import poll_for_answer, extract_codereview_feedback

# --- API Endpoints ---
API_URL = st.secrets["api"]["codereview_presign_api"]
ASK_URL = st.secrets["api"]["ask_url"]
ANSWER_URL = st.secrets["api"]["get_answer_url"]

# --- In-memory Comment Store ---
COMMENTS_DB = {}

def add_comment(user_id, title, code, comment_text):
    timestamp = datetime.now().isoformat()
    COMMENTS_DB.setdefault(title, []).append({
        "user_id": user_id,
        "timestamp": timestamp,
        "code": code,
        "comment": comment_text,
        "votes": 0,
        "voters": []
    })

def load_shared_comments():
    return [
        {**comment, "title": title}
        for title, comment_list in COMMENTS_DB.items()
        for comment in comment_list
    ]

def upvote_comment(timestamp, voter_id):
    for comment_list in COMMENTS_DB.values():
        for comment in comment_list:
            if comment["timestamp"] == timestamp and voter_id not in comment["voters"]:
                comment["votes"] += 1
                comment["voters"].append(voter_id)

# --- OWASP Category Descriptions ---
CATEGORY_DESCRIPTIONS = {
    "A01": "Broken Access Control",
    "A02": "Cryptographic Failures",
    "A03": "Injection",
    "A04": "Insecure Design",
    "A05": "Security Misconfiguration",
    "A06": "Vulnerable and Outdated Components",
    "A07": "Identification and Authentication Failures",
    "A08": "Software and Data Integrity Failures",
    "A09": "Security Logging and Monitoring Failures",
    "A10": "Server-Side Request Forgery (SSRF)"
}

@st.cache_data
def fetch_all_examples_grouped():
    all_filenames = [f"examples/A0{i}.json" for i in range(1, 10)] + ["examples/A10.json"]
    grouped = defaultdict(list)

    for filename in all_filenames:
        payload = {"action": "get", "filename": filename}
        res = requests.post(API_URL, json=payload)

        if res.status_code == 200:
            try:
                url_data = res.json()
                presigned_url = url_data.get("url")
                if presigned_url:
                    s3_res = requests.get(presigned_url)
                    s3_res.raise_for_status()
                    examples = s3_res.json()
                    for ex in examples:
                        cat = ex.get("category", "Unknown")
                        grouped[cat].append(ex)
            except Exception as e:
                st.warning(f"Error parsing {filename}: {e}")
                continue
    return grouped

def render_code_review_tab():
    st.subheader("🔍 Code Review Agent")

    user_id = st.text_input("👤 Student ID", value="student001", key="codereview_uid")

    # Load grouped examples
    grouped_examples = fetch_all_examples_grouped()
    categories = sorted(grouped_examples.keys())

    # Create labels with descriptions
    category_labels = [f"{cat} – {CATEGORY_DESCRIPTIONS.get(cat, '')}" for cat in categories]
    label_to_cat = dict(zip(category_labels, categories))

    selected_label = st.radio("📂 Choose OWASP Category", category_labels, horizontal=True)
    selected_category = label_to_cat[selected_label]

    # Get examples in the selected category
    examples = grouped_examples[selected_category]
    option_labels = [f"{ex['example_id']} – {ex['title']}" for ex in examples]
    selected_label = st.selectbox(f"📚 Select Example from {selected_category}", ["Select one..."] + option_labels)

    if selected_label != "Select one...":
        selected_example = next(
            (ex for ex in examples if f"{ex['example_id']} – {ex['title']}" == selected_label),
            None
        )
        if selected_example:
            default_code = selected_example["code"]
            current_title = selected_example["title"]
            example_id = selected_example["example_id"]
        else:
            default_code = ""
            current_title = "Custom Submission"
            example_id = None
    else:
        default_code = ""
        current_title = "Custom Submission"
        example_id = None

    student_code = st.text_area("💻 Paste your code here", value=default_code, height=300)
    discussion_comment = st.text_area("💬 Comment or question", placeholder="Why is this vulnerable?")

    # Submit comment only
    if st.button("📂 Submit Comment Only"):
        if not student_code.strip():
            st.warning("⚠️ Paste some code first.")
        elif not discussion_comment.strip():
            st.warning("⚠️ Please enter a comment.")
        else:
            add_comment(user_id, current_title, student_code, discussion_comment)
            st.success("✅ Comment submitted.")
            st.rerun()

    # Submit for code review
    if st.button("🧠 Submit for Code Review"):
        if not student_code.strip():
            st.warning("⚠️ Paste some code to review.")
            return

        payload = {
            "user_id": user_id,
            "topic": "codereview",
            "question": student_code
        }

        try:
            with st.spinner("Submitting..."):
                res = requests.post(ASK_URL, json=payload)
                ask_data = res.json()

            request_id = ask_data.get("message", {}).get("request_id")
            if not request_id:
                st.error("❌ No request ID.")
                return

            with st.spinner("Awaiting feedback..."):
                answer = poll_for_answer(ANSWER_URL, request_id, max_attempts=10, delay_sec=3)

            feedback = extract_codereview_feedback(answer)
            st.markdown("### 🧾 Feedback")
            st.markdown(feedback, unsafe_allow_html=True)

            st.session_state.setdefault("history", []).append({
                "title": current_title,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "code": student_code,
                "feedback": feedback,
                "comment": discussion_comment
            })

        except Exception as e:
            st.error(f"❌ Error: {e}")

    # Review History
    with st.expander("🗂️ Review History", expanded=False):
        history = st.session_state.get("history", [])
        if history:
            for entry in reversed(history):
                st.markdown(f"### 📌 {entry['title']} — {entry['timestamp']}")
                st.code(entry["code"], language="javascript")
                if entry.get("comment"):
                    st.markdown(f"💬 *Comment:* {entry['comment']}")
                st.markdown(entry["feedback"], unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No history yet.")

    # Shared Comments
    st.markdown("## 🧠 Shared Comments Board")
    visible_comments = [c for c in load_shared_comments() if c["title"] == current_title]

    if visible_comments:
        for c in sorted(visible_comments, key=lambda x: -x["votes"]):
            st.markdown(f"**👤 {c['user_id']}** — _{c['timestamp']}_")
            st.code(c["code"], language="javascript")
            st.markdown(f"💬 {c['comment']}")
            st.markdown(f"👍 Votes: {c['votes']}")
            if user_id not in c.get("voters", []):
                if st.button("👍 Upvote", key=f"vote_{c['timestamp']}"):
                    upvote_comment(c["timestamp"], user_id)
                    st.rerun()
            else:
                st.markdown("✅ You already voted")
            st.markdown("---")
    else:
        st.info("No shared comments yet for this example.")
