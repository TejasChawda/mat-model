import firebase_admin
from firebase_admin import credentials


def init_db():
    if not firebase_admin._apps:
        cred = credentials.Certificate(
            '/Users/admin/Desktop/pythonStreamlitDemo/ Config/testapp-20a32-firebase-adminsdk-qf29b-35e854714d.json')
        firebase_admin.initialize_app(cred)
