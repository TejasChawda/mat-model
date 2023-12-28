import streamlit as st
import re
import firebase_admin
from firebase_admin import credentials, firestore
from signIn import *
# Check if the Firebase app has been initialized
if not firebase_admin._apps:
    # Initialize Firebase
    cred = credentials.Certificate("/Users/testvagrant/Documents/mat-model/ Config/FBCredentials.json")
    firebase_admin.initialize_app(cred)
# Get a reference to the Firestore database
db = firestore.client()

def userdetails():
    st.title("User Details")
    full_name = st.text_input("Full Name:")
    organization = st.text_input("Organization:")
    designation = st.text_input("Designation:")
    phone_number = st.text_input("Phone Number:")
    if st.button("Submit"):
            # Store user data in Firebase Firestore
            email,id = get_user_details()
            user_data = {
                'id' : id,
                'mail': email,
                'full_name': full_name,
                'organization': organization,
                'designation': designation,
                'phone_number': phone_number,
            }
            # Add a new document to the 'users' collection
            user_ref = db.collection('users').add(user_data)
            st.success(f"Details filled successfully!!")
            full_name = ""
            organization = ""
            designation = ""
            phone_number = ""
            
if __name__ == "__main__":
    userdetails()