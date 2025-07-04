import streamlit as st
import json
import random
import os
import matplotlib.pyplot as plt
from datetime import datetime

def render_tab(uploaded):
    st.header("Tab 2: Quiz")

    path = uploaded.get("quiz")
    if not path:
        st.info("No quiz available.")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
            json_text = raw[raw.find("{"):] if "{" in raw else raw
            quiz_data = json.loads(json_text)

        st.subheader("🧠 Take the Quiz")

        # Reset logic
        if "quiz_answers" not in st.session_state or st.button("🔄 Reset Quiz"):
            st.session_state.quiz_answers = {}

        # Quiz form
        with st.form("quiz_form"):
            for idx, q in enumerate(quiz_data.get("questions", []), 1):
                shuffled = q["choices"][:]
                random.seed(q["question"])  # deterministic shuffle
                random.shuffle(shuffled)

                selected = st.radio(
                    label=f"Q{idx}: {q['question']}",
                    options=shuffled,
                    key=f"quiz_q{idx}"
                )
                st.session_state.quiz_answers[f"q{idx}"] = {
                    "selected": selected,
                    "correct": q["answer"],
                    "explanation": q["explanation"]
                }

            submitted = st.form_submit_button("✅ Submit Answers")

        if submitted:
            st.subheader("📊 Quiz Results")
            score = 0
            total = len(st.session_state.quiz_answers)

            progress = st.progress(0)

            for idx, (qid, data) in enumerate(st.session_state.quiz_answers.items(), 1):
                correct = data["correct"]
                selected = data["selected"]
                explanation = data["explanation"]
                is_correct = (selected == correct)

                st.markdown(f"**Q{idx}:** {'✅ Correct' if is_correct else '❌ Incorrect'}")
                st.markdown(f"- Your answer: `{selected}`")
                st.markdown(f"- Correct answer: `{correct}`")
                st.markdown(f"- 💡 Explanation: {explanation}")
                st.markdown("---")

                if is_correct:
                    score += 1

                progress.progress(idx / total)

            st.success(f"🏁 Final Score: {score} / {total}")

            # Pie chart
            labels = ['✅ Correct', '❌ Incorrect']
            sizes = [score, total - score]
            explode = (0.05, 0)

            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, explode=explode)
            ax.axis('equal')

            st.subheader("📊 Quiz Score Breakdown")
            st.pyplot(fig)

            # Save result to file
            results_dir = "quiz_results"
            os.makedirs(results_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            user_id = st.session_state.get("user_id", "anonymous")
            result_path = os.path.join(results_dir, f"result_{user_id}_{timestamp}.json")

            with open(result_path, "w", encoding="utf-8") as f:
                json.dump({
                    "user_id": user_id,
                    "timestamp": timestamp,
                    "score": score,
                    "total": total,
                    "answers": st.session_state.quiz_answers
                }, f, indent=2)

            st.info(f"📝 Results saved to `{result_path}`")

    except Exception as e:
        st.error(f"⚠️ Failed to parse or display quiz: {e}")
        st.code(raw, language="json")
