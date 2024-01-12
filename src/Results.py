import datetime
import json
import pandas as pd
import plotly.express as px
import paths
import io
import streamlit as st
from firebase_admin import credentials, firestore, initialize_app, get_app
import Session_state
from datetime import datetime, date


state = Session_state.get_session_state()


def show_plotted_graph():
    df = pd.read_csv(paths.read_paths().get('DATA'))
    df['Points'] = df['Points'].str.wrap(30)
    df['Points'] = df['Points'].str.replace('\n', '<br>')
    df['Scale'] = df['Scale'].str.wrap(10)
    df['Scale'] = df['Scale'].str.replace('\n', '<br>')
    df['Value'] = df['Value']
    custom_colors = [
        'rgb(255, 0, 0)',  # Red
        'rgb(255, 80, 0)',  # Orange-Red
        'rgb(255, 120, 0)',  # Orange
        'rgb(255, 180, 0)',  # Orange-Yellow
        'rgb(255, 220, 0)',  # Yellow
        'rgb(200, 220, 0)',  # Yellow-Green
        'rgb(150, 220, 0)',  # Lime Green
        'rgb(0, 128, 0)', 'rgb(0, 128, 0)'
    ]
    fig = px.sunburst(
        data_frame=df,
        path=['Scale', 'Levels', 'Points'],
        values='Value',
        maxdepth=-2,
        width=800,
        height=800,
        color='Value',
        custom_data=['Points', 'Questions'],
        color_continuous_scale=custom_colors,  # Show label, value, and parent on hover
    )
    fig.update_traces(
        textfont_size=12,
        insidetextorientation='radial',
        textinfo='label+text+percent entry',
    )
    fig.update_layout(
        margin=dict(l=10, r=10, b=10, t=10),  # Adjust the values to control spacing
    )
    st.plotly_chart(fig)

    buffer = io.BytesIO()
    fig.write_image(file=buffer, format="pdf")
    st.download_button(
        label="Download PDF",
        data=buffer,
        file_name="figure.pdf",
        mime="application/pdf",
    )


def send_responses_to_database():
    # Replace the path with the correct path to your Firebase Admin SDK JSON file
    cred = credentials.Certificate(
        "/Users/admin/Desktop/pythonStreamlitDemo/ Config/testapp-20a32-firebase-adminsdk-qf29b-35e854714d.json")

    try:
        app = get_app()
    except ValueError:
        app = initialize_app(cred)

    json_file_path = paths.read_paths().get('RESPONSE_JSON')

    with open(json_file_path, 'r') as file:
        json_data = file.read()

    # Convert the list of dictionaries to a JSON-formatted string
    response_string = json.dumps(json_data)

    # Send the entire string to Firestore
    data = {
        'date': str(date.today()),
        'userResponse': response_string
    }

    now = datetime.now()
    formatted_time = now.strftime("%H:%M:%S")
    doc_name = str(formatted_time) + "_" + state.user_id
    db = firestore.client()
    doc_ref = db.collection('user_responses').document(doc_name)
    doc_ref.set(data)


def save_responses_to_json(new_responses, json_file_path):
    try:
        with open(json_file_path, 'r') as json_file:
            existing_responses = json.load(json_file)
    except FileNotFoundError:
        # If the file doesn't exist, initialize with an empty list
        existing_responses = []

    # Append the new responses to the existing ones
    existing_responses.extend(new_responses)

    # Write the combined responses back to the JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(existing_responses, json_file)


def calculate_accuracy():
    earned_values = sum([resp["Value"] for resp in state.responses.values()])
    total_values = len(state.responses) * 50
    accuracy = (earned_values / total_values) * 100 if total_values != 0 else 0
    return accuracy


# def show_history():