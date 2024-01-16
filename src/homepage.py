import streamlit as st
from Session_state import get_session_state
import sidebar
import Results

# Initialize session state
state = get_session_state()


def display_homepage():
    if state.authenticated_user is not None and state.page != "Assessment":
        st.title("Assessment Homepage")
        sidebar.show_sidebar()

        col1, col2 = st.columns(2)

        with col1:
            st.header("Testing Tips")
            st.markdown("- Tip 1: Always read the question carefully.")
            st.markdown("- Tip 2: Be true to yourself.")

            start = st.button("Start Assessment")

            if start:
                state.page = "Assessment"
                st.rerun()

        with col2:
            Results.render_animation()

    else:
        st.warning("User not authenticated. Please log in.")





