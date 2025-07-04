import streamlit as st
from . import tab1_labnotes, tab2_quiz, tab3_solution, tab4_labhint,tab5_code_review

def render_lab_tabs(lab_choice, step_choice, uploaded):
    tab1, tab2, tab3, tab4, tab5= st.tabs(["Practical Notese", "Lab Quiz", "Solution","Hint", "codeReview"])

    with tab1:
        tab1_labnotes.render_tab(uploaded)

    with tab2:
        tab2_quiz.render_tab(uploaded)

    with tab3:
        tab3_solution.render_tab(uploaded)

    with tab4:
        tab4_labhint.render_tab(uploaded)

    with tab5:
        tab5_code_review.render_tab(uploaded)
