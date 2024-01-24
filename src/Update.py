import json
import random

import pandas as pd

import Session_state
import streamlit as st

import Results

state = Session_state.get_session_state()
fil_scales = None


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


def update_level_id():
    accuracy = Results.calculate_accuracy()

    if accuracy > 70:
        new_level_id = int(state.level_id[1:]) + 1
        new_max_level = Session_state.init_level

        if new_level_id > Session_state.max_level:
            state.progress += state.progress_for_each_scale
            update_scale_id()
        elif int(state.level_id[1:]) == 1:
            Session_state.flag = 1
            if new_level_id >= new_max_level:
                state.progress += state.progress_for_each_scale
                update_scale_id()
            state.level_id = f"L{new_level_id}"
        elif Session_state.flag == 1:
            if new_level_id < new_max_level:
                state.level_id = f"{new_level_id}"
            else:
                state.progress += state.progress_for_each_scale
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
            filtered_questions = Session_state.data[
                (Session_state.data["Scale_Id"] == state.scale_id) & (Session_state.data["Level_Id"] == state.level_id)]
            if filtered_questions.empty:
                state.progress += state.progress_for_each_scale
                update_scale_id()
        elif state.level_id == f'L{Session_state.min_level}':
            filtered_questions = Session_state.data[
                (Session_state.data["Scale_Id"] == state.scale_id) & (Session_state.data["Level_Id"] == state.level_id)]
            if filtered_questions.empty:
                state.level_id = f'L{Session_state.min_level + 1}'
        else:
            state.progress += state.progress_for_each_scale
            update_scale_id()

    state.responses = {}
    st.rerun()


def set_up(selected_scales):
    state.page = "Assessment"
    state.available_scale_ids = selected_scales
    state.initial_scale_id = random.choice(selected_scales)
    state.scale_id = state.initial_scale_id
    state.scale_count = len(selected_scales)
    state.progress_for_each_scale = round(100 / state.scale_count)
