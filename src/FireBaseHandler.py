import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("/Users/admin/Desktop/pythonStreamlitDemo/ Config/testapp-20a32-firebase-adminsdk-qf29b-35e854714d.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
data= {

}
doc_ref = db.collection('taskCollection').document()
doc_ref.set(data)
print('hehehe',doc_ref.id)