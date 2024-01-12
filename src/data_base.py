from firebase_admin import credentials, auth, firestore


def initialise_db():
    cred = credentials.Certificate(
        '/Users/admin/Desktop/pythonStreamlitDemo/ Config/testapp-20a32-firebase-adminsdk-qf29b-35e854714d.json')
    firebase_admin.initialize_app(cred)