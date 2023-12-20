import io
import random
import shutil
from datetime import datetime

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import json

config_file_path = '/Users/admin/Desktop/pythonStreamlitDemo/Files/Paths.txt'
config_data = {}

with open(config_file_path, 'r') as file:
    for line in file:
        key, value = line.strip().split('=')
        config_data[key.strip()] = value.strip()

data = pd.read_csv(config_data.get('MODEL'))

copy = shutil.copyfile(config_data.get('MODEL'), config_data.get('DATA'))

init_level = 2

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

# Set the initial scale_id
if 'scale_id' not in st.session_state:
    st.session_state.scale_id = st.session_state.initial_scale_id


OPTIONS_Values = {
    "Regularly": 5,
    "Sometimes": 3,
    "Not Started": 1,
    "Not Applicable": -1,
}

def show_plotted_graph():
    df = pd.read_csv(config_data.get('DATA'))
    df['Points'] = df['Points'].str.wrap(30)
    df['Points'] = df['Points'].str.replace('\n', '<br>')
    df['Scale'] = df['Scale'].str.wrap(10)
    df['Scale'] = df['Scale'].str.replace('\n', '<br>')
    df['Values'] = df['Values'] + 0.01

    custom_colors = [
        'rgb(255, 0, 0)',   # Red
        'rgb(255, 80, 0)',  # Orange-Red
        'rgb(255, 120, 0)', # Orange
        'rgb(255, 180, 0)', # Orange-Yellow
        'rgb(255, 220, 0)', # Yellow
        'rgb(200, 220, 0)', # Yellow-Green
        'rgb(150, 220, 0)', # Lime Green
        'rgb(0, 128, 0)', 'rgb(0, 128, 0)'
    ]

    fig = px.sunburst(
        data_frame=df,
        path=['Scale', 'Levels', 'Points'],
        values='Values',
        maxdepth=-2,
        width=800,
        height=800,
        color='Values',
        custom_data=['Points', 'Questions'],
        color_continuous_scale=custom_colors, # Show label, value, and parent on hover
    )

    fig.update_traces(
        textfont_size=12,
        insidetextorientation='radial',
        textinfo='label+text+percent entry',
    )

    fig.update_layout(
        margin=dict(l=10, r=10, b=10, t=10),  # Adjust the values to control spacing
    )
    st.plotly_chart(fig, use_container_width=True)



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

def update_csv_from_json(json_file_path):
    csv_file_path = config_data.get('MODEL')  # Use the original CSV file path
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
        df.loc[df['Q_Id'] == question_id, 'Values'] = value

    # Write the updated DataFrame back to the original CSV file
    df.to_csv(csv_file_path, index=False)

def calculate_accuracy():
    earned_values = sum([resp["Value"] for resp in st.session_state.responses.values()])
    total_values = len(st.session_state.responses) * 5
    accuracy = (earned_values / total_values) * 100 if total_values != 0 else 0
    return accuracy

def update_level_id():
    accuracy = calculate_accuracy()

    if accuracy > 70:
        new_level_id = int(st.session_state.level_id[1:]) + 1
        if new_level_id > max_level:
            update_scale_id()
        else:
            st.session_state.level_id = f'L{new_level_id}'
    else:
        if st.session_state.level_id == 'L1':
            # Check accuracy for Level 1
            filtered_questions = data[(data["Scale_Id"] == st.session_state.scale_id) & (data["Level_Id"] == 'L1')]
            if not filtered_questions.empty and accuracy < 70:
                st.warning("You did not meet the accuracy threshold for Level 1. Terminating the application.")
                st.stop()
            elif filtered_questions.empty:
                st.session_state.level_id = 'L2'
            # No need to explicitly check accuracy for 'L1' here
        else:
            # Reset to 'L1' if not already in 'L1'
            st.session_state.level_id = 'L1'

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
            key = f"{question['Q_Id']}_{st.session_state.level_id}"  # Use both Q_Id and level_id as a key
            option = form.radio(question["Questions"], list(OPTIONS_Values.keys()), key=key)
            value = OPTIONS_Values[option]

            # Store the response for each question with Question_ID
            st.session_state.responses[key] = {"Question_Id": question['Q_Id'], "Value": value,
                                               "Level_Id": st.session_state.level_id}

        if form.form_submit_button("Submit Responses") and len(
                st.session_state.responses) == len(filtered_questions):
            # Calculate accuracy with the latest responses
            accuracy = calculate_accuracy()
            st.success(f"Responses submitted successfully! Accuracy: {accuracy:.2f}%")

            # new_responses = [
            #     {
            #         "Question_Id": resp["Question_Id"],
            #         "Level_Id": resp["Level_Id"],
            #         "Value": resp["Value"],
            #         "user_id": "u1001",
            #         'timestamp': str(datetime.now())
            #     }
            #     for resp in st.session_state.responses.values()
            # ]

            # Save responses to a JSON file
            json_file_path = config_data.get('RESPONSE_JSON')
            save_responses_to_json(list(st.session_state.responses.values()), json_file_path)
            update_csv_from_json(json_file_path)

            # Move the level update logic outside the form submission block
            update_level_id()

            st.write(f"Updated Level: {st.session_state.level_id}")

if __name__ == "__main__":
    if not st.session_state.available_scale_ids:
        show_plotted_graph()
    else:
        main()
