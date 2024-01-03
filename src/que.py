import os
import random
import shutil
import textwrap

import plotly.express as px
import streamlit as st
import pandas as pd
import json
from firebase_admin import credentials, firestore, initialize_app, get_app

config_file_path = '/Users/admin/Desktop/pythonStreamlitDemo/Files/Paths.txt'
config_data = {}

with open(config_file_path, 'r') as file:
    for line in file:
        key, value = line.strip().split('=')
        config_data[key.strip()] = value.strip()

data = pd.read_csv(config_data.get('MODEL'))

init_level = 2
flag = 0
min_level = 1

levels = data['Levels'].unique()
split_levels = [l.split(" ")[1] for l in levels]
split_levels_int = [int(level) for level in split_levels]
max_level = max(split_levels_int)

scale_ids = list(data['Scale_Id'].unique())

if 'available_scale_ids' not in st.session_state:
    st.session_state.available_scale_ids = scale_ids

# Check if the initial scale_id is already set
if 'initial_scale_id' not in st.session_state:
    # Set the initial scale_id randomly
    st.session_state.initial_scale_id = random.choice(scale_ids)

# Session state initialization
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'level_id' not in st.session_state:
    st.session_state.level_id = f'L{init_level}'
if 'lower_level_modify' not in st.session_state:
    st.session_state.lower_level_modify = False

# Set the initial scale_id
if 'scale_id' not in st.session_state:
    st.session_state.scale_id = st.session_state.initial_scale_id

OPTIONS_Values = {
    "Regularly": 50,
    "Sometimes": 30,
    "Not Started": 10,
    "Not Applicable": 1,
}


def show_plotted_graph():
    df = pd.read_csv(config_data.get('DATA'))
    df['Points'] = df['Scale'].apply(lambda x: textwrap.fill(str(x), width=30))
    df['Points'] = df['Points'].str.replace('\n', '<br>')
    df['Scale'] = df['Scale'].apply(lambda x: textwrap.fill(str(x), width=10))
    df['Scale'] = df['Scale'].str.replace('\n', '<br>')

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
        width=900,
        height=1000,
        color='Value',
        custom_data=['Points', 'Questions'],
        color_continuous_scale=custom_colors,
    )

    st.plotly_chart(fig)


def send_responses_to_database():
    # Replace the path with the correct path to your Firebase Admin SDK JSON file
    cred = credentials.Certificate(
        "/Users/admin/Desktop/pythonStreamlitDemo/ Config/testapp-20a32-firebase-adminsdk-qf29b-35e854714d.json")

    try:
        app = get_app()
    except ValueError:
        app = initialize_app(cred)

    # Assuming config_data is defined somewhere with the path to your JSON file
    json_file_path = config_data.get('RESPONSE_JSON')

    with open(json_file_path, 'r') as file:
        json_data = file.read()

    # Convert the list of dictionaries to a JSON-formatted string
    response_string = json.dumps(json_data)

    # Send the entire string to Firestore
    data = {
        'userResponse': response_string
    }
    db = firestore.client()
    doc_ref = db.collection('user_responses').document()
    doc_ref.set(data)


def update_scale_id():
    if not st.session_state.available_scale_ids:
        st.warning("No more available scale_ids.")
        return

    # Remove the current scale_id from available_scale_ids
    if st.session_state.scale_id in st.session_state.available_scale_ids:
        st.session_state.available_scale_ids.remove(st.session_state.scale_id)

    # Check if there are still available scale_ids
    if not st.session_state.available_scale_ids:
        st.warning("No more available scale_ids.")
        return

    # Choose a new scale_id randomly from the remaining available scale_ids
    chosen_scale_id = random.choice(st.session_state.available_scale_ids)

    # Update session state variables
    st.session_state.scale_id = chosen_scale_id
    st.session_state.level_id = f'L{init_level}'

    # Reset other session state variables if needed
    st.session_state.responses = {}


# def update_levels_below_init_level(data_file_path, scale_id, start):
#     df = pd.read_csv(data_file_path)
#
#     for level in split_levels_int:
#         while level < start:
#             mask = (df['Levels'] == f"level {level}") & (df['Scale_Id'] == scale_id)
#             df[mask, 'Value'] = max(OPTIONS_Values.values())
#
#     df.to_csv(data_file_path, index=False)


def update_csv_from_json(csv_file_path, json_file_path):
    # Read the existing CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    try:
        with open(json_file_path, 'r') as json_file:
            responses = json.load(json_file)
    except FileNotFoundError:
        # If the JSON file doesn't exist, there's nothing to update
        return

    # Update the DataFrame with values from the JSON responses
    for response in responses:
        question_id = response["Question_Id"]
        value = response["Value"]
        # Update the 'Values' column in the DataFrame for the corresponding Question ID
        df.loc[df['Q_Id'] == question_id, 'Value'] = value

    # Write the updated DataFrame back to the original CSV file
    df.to_csv(csv_file_path, index=False)


# def do_update():
#     if st.session_state.lower_level_modify:
#         update_levels_below_init_level(config_data.get('DATA'), st.session_state.scale_id, init_level)
#         st.session_state.lower_level_modify = False


def calculate_accuracy():
    earned_values = sum([resp["Value"] for resp in st.session_state.responses.values()])
    total_values = len(st.session_state.responses) * 5
    accuracy = (earned_values / total_values) * 100 if total_values != 0 else 0
    return accuracy


def update_level_id():
    accuracy = calculate_accuracy()
    global flag

    if accuracy > 70:
        new_level_id = int(st.session_state.level_id[1:]) + 1
        new_max_level = init_level

        if new_level_id > max_level:
            update_scale_id()
        elif int(st.session_state.level_id[1:]) == 1:
            flag = 1
            if new_level_id >= new_max_level:
                update_scale_id()
            st.session_state.level_id = f"L{new_level_id}"
        elif flag == 1:
            if new_level_id < new_max_level:
                st.session_state.level_id = f"{new_level_id}"
            else:
                update_scale_id()
            flag = 0
        else:
            # st.session_state.lower_level_modify = True
            # do_update()
            st.session_state.level_id = f'L{new_level_id}'
    else:
        if int(st.session_state.level_id[1:]) == init_level:
            new_level_id = 1
            st.session_state.level_id = f"L{new_level_id}"
            filtered_questions = data[
                (data["Scale_Id"] == st.session_state.scale_id) & (data["Level_Id"] == st.session_state.level_id)]
            if filtered_questions.empty:
                update_scale_id()
        elif st.session_state.level_id == f'L{min_level}':
            filtered_questions = data[
                (data["Scale_Id"] == st.session_state.scale_id) & (data["Level_Id"] == st.session_state.level_id)]
            if filtered_questions.empty:
                st.session_state.level_id = f'L{min_level + 1}'
        else:
            update_scale_id()

    st.session_state.responses = {}
    st.rerun()


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


def main():
    shutil.copyfile(config_data.get('MODEL'), config_data.get('DATA'))

    st.title("Testing Assessment")
    st.write(st.session_state.level_id + " - " + st.session_state.scale_id)

    form = st.form(key='questionnaire_form')
    filtered_questions = data[
        (data["Scale_Id"] == st.session_state.scale_id) & (data["Level_Id"] == st.session_state.level_id)]

    if filtered_questions.empty:
        st.warning("No questions found for the provided Scale ID and Level ID.")
        update_level_id()
    else:
        for _, question in filtered_questions.iterrows():
            widget_key = f"{question['Q_Id']}_{st.session_state.level_id}"  # Use both Q_Id and level_id as a key
            option = form.radio(question["Questions"], list(OPTIONS_Values.keys()), key=widget_key)

            # if option is not None:
            option_values = OPTIONS_Values[option]

            # Store the response for each question with Question_ID
            st.session_state.responses[widget_key] = {"Question_Id": question['Q_Id'], "Value": option_values,
                                                      "Level_Id": st.session_state.level_id,
                                                      "Scale": st.session_state.scale_id}

        # Outside the for loop
        if form.form_submit_button("Submit Responses") and len(st.session_state.responses) == len(filtered_questions):
            # Calculate accuracy with the latest responses
            accuracy = calculate_accuracy()
            st.success(f"Responses submitted successfully! Accuracy: {accuracy:.2f}%")

            # Save responses to a JSON file
            json_file_path = config_data.get('RESPONSE_JSON')
            save_responses_to_json(list(st.session_state.responses.values()), json_file_path)
            update_csv_from_json(config_data.get('DATA'), json_file_path)

            # Move the level update logic outside the form submission block
            update_level_id()

            st.write(f"Updated Level: {st.session_state.level_id}")


if __name__ == "__main__":
    if not st.session_state.available_scale_ids:
        show_plotted_graph()
        send_responses_to_database()
    else:
        main()
