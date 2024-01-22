import streamlit as st
import Session_state
import Results

state = Session_state.get_session_state()


def show_sidebar():
    profile_picture_link = "https://images.unsplash.com/photo-1682685797439-a05dd915cee9?q=80&w=2787&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDF8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    round_image_style = """
    <style>
        img {
            border-radius: 50%;
            max-width: 150px;
            max-height: 150px;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
    """
    st.markdown(round_image_style, unsafe_allow_html=True)
    st.sidebar.image(profile_picture_link, caption="Your Profile Picture", use_column_width=True)
    logged_in_user = str(state.authenticated_user)
    st.sidebar.text(" Hello 👋 "+logged_in_user)
    if state.page == "Homepage":
        if st.sidebar.button("History"):
            Results.custom_loader("Please wait while we fetch your data....")
            state.page = "History"
            st.rerun()
    elif state.page == "History":
        if st.sidebar.button("Homepage"):
            state.page = "Homepage"
            st.rerun()

    if st.sidebar.button("Logout"):
        print(state.authenticated_user+" is"+" Logged out successfully!")
        state.initialized = True
        state.authenticated_user = None
        state.user_id = None
        state.responses = {}
        state.page = "Login"
        st.rerun()

