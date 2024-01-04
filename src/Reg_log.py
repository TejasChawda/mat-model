import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import re
import homepage
from Session_state import get_session_state
from streamlit_option_menu import option_menu

state = get_session_state()


def validate_email(mail_id):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, mail_id)


def validate_password(pwd):
    return len(pwd) >= 8


def authenticate_user(mail):
    try:
        user = auth.get_user_by_email(mail)
        if user is not None:
            state.authenticated_user = user
            state.page = "Homepage"
            st.experimental_rerun()
        else:
            st.write("something is wrong")
    except auth.UserNotFoundError:
        st.warning("User not found. Please register first.")
    except Exception as e:
        st.error(f"Authentication failed: {e}")


def register_user(mail, pwd):
    try:
        user = auth.create_user(email=mail, password=pwd)
        st.success("Registration successful!")
        return user
    except Exception as e:
        st.error(f"User registration failed: {e}")


def login_view():
    st.subheader("Login")
    email = st.text_input('Email:')
    password = st.text_input('Password:', type='password')
    login_button = st.button('Login')

    if login_button:
        authenticate_user(email)


def register_view():
    st.title("Sign Up")
    full_name = st.text_input("Full Name:")
    organization = st.text_input("Organization:")
    email = st.text_input("Email:")

    if email != "" and not validate_email(email):
        st.warning("Invalid email format. Please enter a valid email.")
    phone_number = st.text_input("Phone Number:")
    password = st.text_input("Password:", type="password")

    if password != "" and not validate_password(password):
        st.warning("Password must be at least 8 characters long.")
    confirm_password = st.text_input("Confirm Password:", type="password")
    register_button = st.button('Register')

    if register_button:
        if password == confirm_password:
            register_user(email, password)
        else:
            st.error("Password and Confirm Password do not match. Please try again.")


if not firebase_admin._apps:
    cred = credentials.Certificate('/Users/admin/Desktop/pythonStreamlitDemo/ '
                                   'Config/testapp-20a32-firebase-adminsdk-qf29b-35e854714d.json')
    firebase_admin.initialize_app(cred)

st.title('Firebase Authentication with Streamlit')

selected_option = option_menu(
    menu_title=None,
    options=["Register", "Login"],
    icons=["door-open", "box-arrow-in-right"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

if selected_option == "Login":
    login_view()
elif selected_option == "Register":
    register_view()

# Check the authentication status and render the homepage if authenticated
if state.page == "Homepage":
    homepage.main()
