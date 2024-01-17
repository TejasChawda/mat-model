# import database
#
# database.init_db()
# import streamlit as st
# import Results
# import paths
#

import streamlit as st
from firebase_admin import firestore
import database


def show_ui():
    st.title("View Previous Assessment!")

    # Centered text
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; height: 150px;">
        <h3>Select Date of assessment taken</h3>
    </div>
    """, unsafe_allow_html=True)

    # Custom dropdown
    selected_option = st.selectbox("", ["Option 1", "Option 2", "Option 3"])

    # Submit button
    if st.button("Submit"):
        st.success(f"Selected option: {selected_option}")


def retrieve_data():
    database.init_db()
    db = firestore.client

