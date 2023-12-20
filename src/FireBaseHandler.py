import time

import firebase_admin
from firebase_admin import credentials, db


class FirebaseHandler:
    def __init__(self, credentials_file, database_url, app_name='default'):
        # Check if the app is already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(credentials_file)
            firebase_admin.initialize_app(
                cred,
                {
                    "databaseURL": database_url
                },
                name=app_name
            )
        self.ref = db.reference("/")

    def push_response_to_db(self, user_id, responses):
        user_ref = self.ref.child(user_id)
        user_ref.push().set(responses)

    def get_user_responses_from_db(self, user_id):
        retrieved_data = self.ref.child(user_id).get()
        return retrieved_data

    def close_connection(self):
        firebase_admin.delete_app(firebase_admin.get_app())


if __name__ == "__main__":
    credentials_file = "/Users/admin/Desktop/pythonStreamlitDemo/ Config/FBCredentials.json"
    database_url = "https://maturitymodel-cf384-default-rtdb.asia-southeast1.firebasedatabase.app/"
    firebase_handler = FirebaseHandler(credentials_file, database_url)
    user_id = "u1001"
    response_data = [
        {
            "updatedTime": time.strftime("%d-%m-%Y-%H-%M", time.localtime()),
            "scale_id": "TC",
            "level_id": "L3",
            "qid": "Q14",
            "response": "Regularly",
            "Value": 5,
        }
    ]
    # Push data to Firebase
    firebase_handler.push_response_to_db(user_id, response_data)
    # Retrieve and print data from Firebase
    # firebase_handler.get_users_response(user_id)
    # Close the Firebase connection
    firebase_handler.close_connection()
