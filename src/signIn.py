import streamlit as st
from auth import *
from userdetails import *

def sign_in():
    st.title("Sign In")
    # email = st.text_input("Email:", key="email_input")
    # password = st.text_input("Password:", type="password", key="password_input")
    
    # if st.button("Sign In"):
    #     st.success(f"Signed in with Email: {email}")

    login_button_html = get_login_str()
    login_button_style = """
            display: inline-block;
            padding: 8px;
            background-color: white;
            text-align: center;
            font-size: 14px;
            margin-bottom: 6px;
            border: 1px solid black;
            border-radius: 5px;
            cursor: pointer;
    """

    link = st.markdown(f'<div style="{login_button_style}">{login_button_html}</div>', unsafe_allow_html=True)
    if link :
        userdetails()


if __name__ == "__main__":
    sign_in()
