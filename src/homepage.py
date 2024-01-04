import streamlit as st
from Session_state import get_session_state

state = get_session_state()


def main():

    st.title("Assessment Homepage")

    if state.authenticated_user is not None:
        logged_in_user = str(state.authenticated_user.display_name)
        user_clicked = st.sidebar.button(logged_in_user, key="user_button")
        if user_clicked:
            profile_options()

        st.header("Testing Tips")
        st.markdown("- Tip 1: Always read the question carefully.")
        st.markdown("- Tip 3: Double-check your answers before submitting.")

        if st.button("Start Assessment"):
            st.success("Assessment Started! Good luck!")

    else:
        st.warning("User not authenticated. Please log in.")


def profile_options():
    if st.sidebar.button("History"):
        st.success("History Clicked!")
        # Add any additional actions related to history

    if st.sidebar.button("Logout"):
        st.success("Logged out successfully!")
        state.authenticated_user = None
        state.page = "Login"
