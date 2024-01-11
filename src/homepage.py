import streamlit as st
from Session_state import get_session_state
import sidebar


# Initialize session state
state = get_session_state()


def display_homepage():
    if state.authenticated_user is not None and state.page != "Assessment":
        st.title("Assessment Homepage")
        sidebar.show_sidebar()

        st.header("Testing Tips")
        st.markdown("- Tip 1: Always read the question carefully.")
        st.markdown("- Tip 3: Double-check your answers before submitting.")

        start = st.button("Start Assessment")

        if start:
            state.page = "Assessment"
            st.rerun()
    else:
        st.warning("User not authenticated. Please log in.")





