import json

import streamlit as st
from firebase_admin import firestore
import database
import Results
import paths
import Update

document_ids = []
database.init_db()
db = firestore.client()
uid = 'E1a64bLgyHSDGak3MyCfoXMYwan1'


def retrieve_data():
    global document_ids  # Correct way to get the Firestore client
    collection_ref = db.collection(f'user_responses/{uid}/dates')
    documents = collection_ref.stream()
    for doc in documents:
        print(f"Document Name: {doc.id}")
    documents = collection_ref.stream()
    document_ids = [doc.id for doc in documents]
    return document_ids


def display_graph(selected_opt):
    doc_path = f'user_responses/{uid}/dates/{selected_opt}'
    doc_ref = db.document(doc_path)
    doc_snapshot = doc_ref.get()
    response = doc_snapshot.get("userResponse")
    print(response)
    json_resp = json.loads(response)

    json_file = paths.read_paths().get('RESPONSE_JSON')

    with open(json_file, 'w') as json_file:
        json_file.write('')
        json_file.write(json_resp)
    Update.update_csv_from_json(paths.read_paths().get('DATA'), paths.read_paths().get('RESPONSE_JSON'))
    Results.show_plotted_graph()


def main():
    st.title("View Previous Assessment!")

    # Centered text
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; height: 150px;">
        <h3>Select Date of assessment taken</h3>
    </div>
    """, unsafe_allow_html=True)

    all_dates = retrieve_data()
    selected_option = st.selectbox("", all_dates)

    # Submit button
    if st.button("Submit"):
        st.success(f"Selected option: {selected_option}")
        display_graph(selected_option)
