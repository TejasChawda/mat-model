import streamlit as st
import Session_state

state = Session_state.get_session_state()


def show_sidebar():
    st.sidebar.text(" Hello 👋")
    logged_in_user = str(state.authenticated_user)
    user_clicked = st.sidebar.button(logged_in_user, key="user_button")
    if user_clicked:
        profile_options()


def profile_options():
    if st.sidebar.button("History"):
        state.page = "History"
        st.rerun()

    if st.sidebar.button("Logout"):
        st.success("Logged out successfully!")
        state.authenticated_user = None
        state.page = "Login"
