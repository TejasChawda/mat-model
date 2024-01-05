import streamlit as st


def get_session_state():
    if not hasattr(st.session_state, "initialized"):
        st.session_state.initialized = True
        st.session_state.authenticated_user = None
        st.session_state.page = "Login"
        st.session_state.logged_in = False
        st.session_state.assessment = False

    return st.session_state
