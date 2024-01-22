import streamlit as st
from Session_state import get_session_state
import sidebar
import Results
import paths
import history
import Session_state
import Update

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

            # selected_scales = st.multiselect("Select the scales :", Session_state.scale_ids)
            # scales = Update.update_available_scales(selected_scales)
            # state.available_scale_ids = scales

            start = st.button("Start Assessment")

            if start:
                Results.spinner("Please wait while we are loading Questions", 2)
                state.page = "Assessment"
                st.rerun()

        with col2:
            Results.render_animation(paths.read_paths().get("HELLO_ANIMATION"), 500, 600)

    else:
        st.warning("User not authenticated. Please log in.")
