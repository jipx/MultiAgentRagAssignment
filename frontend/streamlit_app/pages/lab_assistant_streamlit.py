import streamlit as st

# Simulated data (replace with actual KB calls)
lab_notes = {
    "lab1": [
        "Understand how input is handled in SQL queries.",
        "Identify unsanitized user inputs in SQL strings.",
        "Replace raw queries with prepared statements."
    ],
    "lab2": [
        "Analyze how HTML and JavaScript are rendered from user input.",
        "Test for script injection points in forms.",
        "Implement proper encoding and CSP headers."
    ],
    "lab3": [
        "Review password storage mechanism.",
        "Test login endpoints for brute-force protection.",
        "Add MFA and lockout policies."
    ]
}

quiz_questions = {
    "lab1": [
        {
            "type": "mcq",
            "question": "What is a common SQL injection technique?",
            "options": ["Union-based", "Phishing", "Clickjacking"],
            "answer": "Union-based",
            "explanation": "Union-based SQL injection appends a UNION clause to extract data."
        },
        {
            "type": "fill",
            "question": "Fill in the blank: Always use _____ statements to avoid SQL injection.",
            "answer": "prepared",
            "explanation": "Prepared statements prevent SQL injection by separating data from code."
        }
    ],
    "lab2": [
        {
            "type": "mcq",
            "question": "What does XSS target?",
            "options": ["Client browser", "Server logs", "Database"],
            "answer": "Client browser",
            "explanation": "XSS executes malicious scripts in the user's browser."
        },
        {
            "type": "fill",
            "question": "Fill in the blank: A key mitigation for XSS is using _____ headers.",
            "answer": "CSP",
            "explanation": "Content Security Policy (CSP) headers help restrict allowed sources for scripts."
        }
    ]
}

st.set_page_config(page_title="Lab Assistant", layout="wide")
st.title("🧪 Lab Assistant")

# Sidebar selections
lab_id = st.sidebar.selectbox("Select Lab", list(lab_notes.keys()))
step_index = st.sidebar.selectbox("Select Step", range(1, len(lab_notes[lab_id]) + 1))

# Tabs for full notes, Q&A, hints, and quiz
tab1, tab2, tab3, tab4 = st.tabs(["📘 View Full Notes", "💬 Ask Assistant", "💡 Generate Hint", "📝 Quiz"])

with tab1:
    st.subheader(f"Complete Notes for {lab_id.upper()}")
    for i, step in enumerate(lab_notes[lab_id]):
        st.markdown(f"### Step {i + 1}\n{step}")

with tab2:
    question = st.text_input("Ask a question about this step:")
    if st.button("Submit Question"):
        st.success(f"Claude 3 Response: '{question}' relates to Step {step_index}. Use prepared statements.")

with tab3:
    if st.button("Generate Hint"):
        st.info(f"Hint: Review Step {step_index} and check for direct use of user input in the logic.")

with tab4:
    st.subheader(f"Quiz for {lab_id.upper()}")
    score = 0
    total = 0
    responses = {}
    if lab_id in quiz_questions:
        for i, q in enumerate(quiz_questions[lab_id]):
            total += 1
            st.markdown(f"**Q{i+1}: {q['question']}**")
            if q["type"] == "mcq":
                selected = st.radio("", q["options"], key=f"q{i}")
                responses[f"q{i}"] = selected == q["answer"]
            elif q["type"] == "fill":
                answer = st.text_input("", key=f"q{i}")
                responses[f"q{i}"] = answer.strip().lower() == q["answer"].lower()
        if st.button("Submit Quiz"):
            score = sum(responses.values())
            st.success(f"You scored {score} out of {total}.")
            for i, q in enumerate(quiz_questions[lab_id]):
                if not responses[f"q{i}"]:
                    st.error(f"Q{i+1} Explanation: {q['explanation']}")
    else:
        st.info("No quiz available for this lab.")
