import streamlit as st

def render_tab(uploaded):
    st.header("Tab 1: Lab Notes")

    path = uploaded.get("labnotes")
    if not path:
        st.info("No lab notes uploaded.")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # ✅ Render the content as Markdown
        st.markdown(content, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ Could not load lab notes: {e}")
