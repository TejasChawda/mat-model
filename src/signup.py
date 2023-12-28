import streamlit as st
from signIn import sign_in
from que import main
import re

def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

def validate_password(password):
    return len(password) >= 8

def signup():
    st.title("Sign Up")
    full_name = st.text_input("Full Name:")
    organization = st.text_input("Organization:")
    email = st.text_input("Email:")
    if not validate_email(email):
        st.error("Invalid email format. Please enter a valid email.")
        return
    phone_number = st.text_input("Phone Number:")
    password = st.text_input("Password:", type="password")
    if not validate_password(password):
        st.error("Password must be at least 8 characters long.")
        return
    confirm_password = st.text_input("Confirm Password:", type="password")
    if st.button("Sign Up"):
        if password == confirm_password:
            st.success(f"Signed up Successfully")
            st.button("Go to Sign In", key="go_to_signin")
            execute_second_script()

def execute_second_script():
    # Include the logic of your second script here
    st.rerun()

if __name__ == "__main__":
    if "go_to_signin" in st.session_state:
        main()
    else:
        signup()
