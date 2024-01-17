import bcrypt
import streamlit as st
import re
from Session_state import get_session_state
from streamlit_option_menu import option_menu
from firebase_admin import auth, firestore
import homepage
import Application
import Results
import database
import history

state = get_session_state()


def encrypt_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(entered_password, stored_password):
    # Check if the entered password matches the stored hashed password
    return bcrypt.checkpw(entered_password.encode('utf-8'), stored_password.encode('utf-8'))


# Initialize Firebase Admin SDK
# if not firebase_admin._apps:
#     cred = credentials.Certificate(
#         '/Users/admin/Desktop/pythonStreamlitDemo/ Config/testapp-20a32-firebase-adminsdk-qf29b-35e854714d.json')
#     firebase_admin.initialize_app(cred)

database.init_db()

# Initialize Firestore
db = firestore.client()


def validate_email(mail_id):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, mail_id)


def validate_password(pwd):
    return len(pwd) >= 8


def login_view():
    st.subheader("Login")
    email = st.text_input('Email:')
    password = st.text_input('Password:', type='password')

    # Center the button and give it a larger width
    st.markdown("""
    <style>
        div.stButton > button {
            width: 200px;
            margin: 0 auto;
            display: block;
        }
    </style>
    """, unsafe_allow_html=True)

    # Create the centered and wider button
    if st.button('Login'):
        if email != "":
            st.balloons()
            uem = login(email, password)
            state.authenticated_user = uem.email
            state.user_id = uem.uid
            # Results.custom_loader("Loading.....")
            state.page = "Homepage"
            st.rerun()
        else:
            st.warning("please provide your credentials")


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

    # Center the button and give it a larger width
    st.markdown("""
    <style>
        div.stButton > button {
            width: 200px;
            margin: 0 auto;
            display: block;
        }
    </style>
    """, unsafe_allow_html=True)

    # Create the centered and wider button
    register_button = st.button('Register')

    if register_button:
        if password == confirm_password:
            st.balloons()
            user_object = signup(email, password, full_name, phone_number, organization)
            state.authenticated_user = user_object["email"]
            state.user_id = user_object["uid"]
            state.page = "Homepage"
            st.rerun()
        else:
            st.error("Password and Confirm Password do not match. Please try again.")


def signup(email, password, name, ph, org):
    try:
        # Create user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password,
        )
        # Create a new document in the 'users' collection
        user_ref = db.collection('users').document(user.uid)
        user_ref.set({
            'email': email,
            'name': name,
            'password': encrypt_password(password),
            'phone_number': ph,
            'organization': org
            # Add more fields as needed
        })
        print(f"User {email} successfully created with ID: {user.uid}")
        uem = {
                'email':email,
                'uid':user.uid
               }
        return uem
    except Exception as e:
        print(f"Error creating user: {e}")


def login(email, password):
    try:
        # Get user by email from Firebase Authentication
        user = auth.get_user_by_email(email)
        # Check if the user document exists in the 'users' collection
        user_ref = db.collection('users').document(user.uid)
        user_data = user_ref.get()
        if not user_data.exists:
            print("User does not exist. Please sign up.")
            return
        # Get the stored password from the Firestore document
        stored_password = user_data.get('password')
        # Compare the provided password with the stored password
        if verify_password(password, stored_password):
            print(f"User {email} successfully authenticated.")
            return user
        else:
            print("Incorrect password.")
    except auth.UserNotFoundError:
        print("User not found. Please sign up.")
    except Exception as e:
        print(f"Error during login: {e}")


if state.page == "Homepage":
    homepage.display_homepage()
elif state.page == "History":
    history.main()
elif state.page == "Assessment":
    Application.main()
elif state.page == "Graph":
    Results.show_plotted_graph()
    Results.send_responses_to_database()
else:
    st.title('User authentication')
    selected_option = option_menu(
        menu_title=None,
        options=["Login", "Register"],
        icons=["door-open", "box-arrow-in-right"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )
    if selected_option == "Login":
        login_view()
    elif selected_option == "Register":
        register_view()
