import streamlit as st
from Session_state import get_session_state
import sidebar
import Results
import paths
import Session_state
import Csv
import Update
import Json

# Initialize session state
state = get_session_state()


def display_homepage():
    if state.authenticated_user is not None and state.page != "Assessment":
        st.title("Assessment Homepage")
        sidebar.show_sidebar()
        Csv.clear_csv(paths.read_paths().get('DATA'))
        Json.clear_json(paths.read_paths().get('RESPONSE_JSON'))

        col1, col2 = st.columns(2)

        with col1:
            st.header("Testing Tips")
            st.markdown("- Tip 1: Always read the question carefully.")
            st.markdown("- Tip 2: Be true to yourself.")

            selected_scales = st.multiselect("Select the scales :", Session_state.scale_ids)

            start = st.button("Start Assessment")

            if start:
                if selected_scales:
                    Results.spinner("Please wait while we are loading Questions", 2)
                    Update.set_up(selected_scales)
                    Csv.filter_csv(Session_state.scale_ids, selected_scales, paths.read_paths().get('MODEL'),
                                   paths.read_paths().get('DATA'))
                    st.rerun()
                else:
                    st.warning("PLease Select your preferred scales")
        with col2:
            Results.render_animation(paths.read_paths().get("HELLO_ANIMATION"), 500, 600)

    else:
        st.warning("User not authenticated. Please log in.")
