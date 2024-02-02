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

    if state.scale_id in state.available_scale_ids:
        state.available_scale_ids.remove(state.scale_id)

    if not state.available_scale_ids:
        st.warning("No more available Session_state.scale_ids.")
        return

    chosen_scale_id = random.choice(state.available_scale_ids)

    state.scale_id = chosen_scale_id
    state.level_id = f'L{Session_state.init_level}'

    state.responses = {}


def update_csv_from_json(csv_file_path, json_file_path):
    df = pd.read_csv(csv_file_path)

    try:
        with open(json_file_path, 'r') as json_file:
            responses = json.load(json_file)
    except FileNotFoundError:
        return

    for response in responses:
        question_id = response["Question_Id"]
        value = response["Value"]
        df.loc[df['Q_Id'] == question_id, 'Value'] = value

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
        else:
            state.progress += state.progress_for_each_scale
            update_scale_id()

    state.responses = {}
    st.rerun()


def set_up(selected_scales):
    state.responses = {}
    state.page = "Assessment"
    state.level_id = f'L{Session_state.init_level}'
    state.available_scale_ids = selected_scales
    state.initial_scale_id = random.choice(selected_scales)
    state.scale_id = state.initial_scale_id
    state.scale_count = len(selected_scales)
    state.progress = 0
    state.progress_for_each_scale = round(100 / state.scale_count)