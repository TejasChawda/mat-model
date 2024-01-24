import json
import sidebar
import streamlit as st
from firebase_admin import firestore
import database
import Results
import paths
import Update
import Session_state
import Json
import Csv

document_ids = []
database.init_db()
db = firestore.client()

state = Session_state.get_session_state()


def retrieve_data():
    global document_ids  # Correct way to get the Firestore client

    collection_ref = db.collection(f'user_responses/{str(state.user_id)}/dates')
    documents = collection_ref.stream()
    document_ids = [doc.id for doc in documents]
    return document_ids


def display_graph(selected_opt):
    doc_path = f'user_responses/{str(state.user_id)}/dates/{selected_opt}'
    doc_ref = db.document(doc_path)
    doc_snapshot = doc_ref.get()
    response = doc_snapshot.get("userResponse")
    json_resp = json.loads(response)

    json_file = paths.read_paths().get('RESPONSE_JSON')

    with open(json_file, 'w') as json_file:
        json_file.write(json_resp)

    scales = Json.get_scales_from_json(paths.read_paths().get('RESPONSE_JSON'))
    Csv.filter_csv(Session_state.scale_ids, scales, paths.read_paths().
                   get('MODEL'), paths.read_paths().
                   get('DATA'))
    Update.update_csv_from_json(paths.read_paths().get('DATA'), paths.read_paths().get('RESPONSE_JSON'))
    Results.show_plotted_graph()


def display_history():
    all_dates = retrieve_data()
    sidebar.show_sidebar()

    col2, col3 = st.columns(2)

    with col2:
        st.title("View Assessment History")
    with col3:
        Results.render_animation(paths.read_paths().get('DB_ANIMATION'), 250, 200)

    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; height: 150px;">            
    <h3>Select Date of assessment taken</h3>
    </div>
    """, unsafe_allow_html=True)

    selected_option = st.selectbox("", all_dates)

    # Submit button
    if st.button("Submit"):
        st.success(f"Selected option: {selected_option}")
        display_graph(selected_option)