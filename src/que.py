import io
import random
import plotly.express as px
import streamlit as st
import pandas as pd
import json
from firebase_admin import credentials, firestore, initialize_app, get_app
import options
import form_decorators
import paths
import data_frame
import Session_state

state = Session_state.get_session_state()

data = pd.read_csv(paths.read_paths().get('MODEL'))

levels = data_frame.get_levels(data)
max_level = data_frame.get_max_level(levels)

scale_count = len(Session_state.scale_ids)
level_count = len(levels)
total_pages = scale_count * level_count


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
        'userResponse': response_string
    }
    db = firestore.client()
    doc_ref = db.collection('user_responses').document()
    doc_ref.set(data)


def update_scale_id():
    if not state.available_scale_ids:
        st.warning("No more available Session_state.scale_ids.")
        return

    # Remove the current scale_id from available_Session_state.scale_ids
    if state.scale_id in state.available_scale_ids:
        state.available_scale_ids.remove(state.scale_id)


    # Check if there are still available Session_state.scale_ids
    if not state.available_scale_ids:
        st.warning("No more available Session_state.scale_ids.")
        return

    # Choose a new scale_id randomly from the remaining available Session_state.scale_ids
    chosen_scale_id = random.choice(state.available_scale_ids)

    # Update session state variables
    state.scale_id = chosen_scale_id
    state.level_id = f'L{Session_state.init_level}'

    # Reset other session state variables if needed
    state.responses = {}


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


def calculate_accuracy():
    earned_values = sum([resp["Value"] for resp in state.responses.values()])
    total_values = len(state.responses) * 50
    accuracy = (earned_values / total_values) * 100 if total_values != 0 else 0
    return accuracy


def update_level_id():
    accuracy = calculate_accuracy()

    if accuracy > 70:
        new_level_id = int(state.level_id[1:]) + 1
        new_max_level = Session_state.init_level

        if new_level_id > max_level:
            update_scale_id()
        elif int(state.level_id[1:]) == 1:
            Session_state.flag = 1
            if new_level_id >= new_max_level:
                update_scale_id()
            state.level_id = f"L{new_level_id}"
        elif Session_state.flag == 1:
            if new_level_id < new_max_level:
                state.level_id = f"{new_level_id}"
            else:
                update_scale_id()
            Session_state.flag = 0
        else:
            # state.lower_level_modify = True
            # do_update()
            state.level_id = f'L{new_level_id}'
    else:
        if int(state.level_id[1:]) == Session_state.init_level:
            new_level_id = 1
            state.level_id = f"L{new_level_id}"
            filtered_questions = data[
                (data["Scale_Id"] == state.scale_id) & (data["Level_Id"] == state.level_id)]
            if filtered_questions.empty:
                update_scale_id()
        elif state.level_id == f'L{Session_state.min_level}':
            filtered_questions = data[
                (data["Scale_Id"] == state.scale_id) & (data["Level_Id"] == state.level_id)]
            if filtered_questions.empty:
                state.level_id = f'L{Session_state.min_level + 1}'
        else:
            update_scale_id()

    state.responses = {}
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
    st.write(state.level_id + " - " + state.scale_id)

    form = st.form(key='questionnaire_form')
    filtered_questions = data[
        (data["Scale_Id"] == state.scale_id) & (data["Level_Id"] == state.level_id)]

    if filtered_questions.empty:
        st.warning("No questions found for the provided Scale ID and Level ID.")
        update_level_id()
    else:

        for _, question in filtered_questions.iterrows():
            widget_key = f"{question['Q_Id']}_{state.level_id}"  # Use both Q_Id and level_id as a key
            option = form.radio(question["Questions"], list(choice.name for choice in options.Options), key=widget_key)

            # if option is not None:
            selected_option = options.Options[option] if option else None
            option_values = selected_option.value if selected_option else None

            # Store the response for each question with Question_ID
            state.responses[widget_key] = {"Question_Id": question['Q_Id'], "Value": option_values,
                                                      "Level_Id": state.level_id,
                                                      "Scale": state.scale_id}

        # Outside the for loop
        if form.form_submit_button("Submit Responses") and len(state.responses) == len(filtered_questions):
            form_decorators.loader("Submitting.........")
            state.current_page += 1

            # Calculate accuracy with the latest responses
            accuracy = calculate_accuracy()
            st.success(f"Responses submitted successfully! Accuracy: {accuracy:.2f}%")

            # Save responses to a JSON file
            json_file_path = paths.read_paths().get('RESPONSE_JSON')
            save_responses_to_json(list(state.responses.values()), json_file_path)
            update_csv_from_json(paths.read_paths().get('DATA'), json_file_path)

            # Move the level update logic outside the form submission block
            update_level_id()

            st.write(f"Updated Level: {state.level_id}")


if __name__ == "__main__":
    if not state.available_scale_ids:
        show_plotted_graph()
        send_responses_to_database()
    else:
        main()
