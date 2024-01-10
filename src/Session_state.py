import random

import pandas as pd
import streamlit as st

import data_frame
import paths

init_level = 2
flag = 0
min_level = 1

data = pd.read_csv(paths.read_paths().get('MODEL'))

s_ids = data_frame.get_scale_ids(data)
scale_ids = list(s_ids)

levels = data_frame.get_levels(data)
max_level = data_frame.get_max_level(levels)


def get_session_state():
    if not hasattr(st.session_state, "initialized"):
        st.session_state.initialized = True
        st.session_state.authenticated_user = None
        st.session_state.page = "Login"
        st.session_state.logged_in = False
        st.session_state.assessment = False
        st.session_state.available_scale_ids = scale_ids
        st.session_state.current_page = 1
        st.session_state.initial_scale_id = random.choice(scale_ids)
        st.session_state.responses = {}
        st.session_state.level_id = f'L{init_level}'
        st.session_state.scale_id = st.session_state.initial_scale_id

    return st.session_state
