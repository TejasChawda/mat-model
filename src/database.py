import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import Session_state

state = Session_state.get_session_state()
document_ids = []


def init_db():
    if not firebase_admin._apps:
        cred = credentials.Certificate(
            '/Users/admin/Desktop/pythonStreamlitDemo/Config/testapp-20a32-firebase-adminsdk-qf29b-35e854714d.json')
        firebase_admin.initialize_app(cred)


init_db()
db = firestore.client()


def retrieve_data(selected_opt):
    doc_path = f'user_responses/{str(state.user_id)}/dates/{selected_opt}'
    doc_ref = db.document(doc_path)
    doc_snapshot = doc_ref.get()
    response = doc_snapshot.get("userResponse")
    json_resp = json.loads(response)

    return json_resp


def retrieve_dates():
    global document_ids

    collection_ref = db.collection(f'user_responses/{str(state.user_id)}/dates')
    documents = collection_ref.stream()
    document_ids = [doc.id for doc in documents]

    return document_ids
