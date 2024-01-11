import streamlit as st

import Session_state

state = Session_state.get_session_state()


def show_sidebar():
    logged_in_user = str(state.authenticated_user.split('@')[0])
    user_clicked = st.sidebar.button(logged_in_user, key="user_button")
    if user_clicked:
        profile_options()


def profile_options():
    if st.sidebar.button("History"):
        st.success("History Clicked!")

    if st.sidebar.button("Logout"):
        st.success("Logged out successfully!")
        state.authenticated_user = None
        state.page = "Login"
