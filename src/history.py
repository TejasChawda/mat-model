import json
import sidebar
import streamlit as st
import Results
import paths
import Update
import Session_state
import Json
import Csv
import database

state = Session_state.get_session_state()


def display_graph(selected_opt):

    json_resp = database.retrieve_data(selected_opt)

    json_file = paths.read_paths().get('RESPONSE_JSON')

    with open(json_file, 'w') as json_file:
        json_file.write(json_resp)

    scales = Json.get_scales_from_json(paths.read_paths().get('RESPONSE_JSON'))
    Csv.filter_csv(Session_state.scale_ids, scales, paths.read_paths().
                   get('MODEL'), paths.read_paths().
                   get('DATA'))
    Update.update_csv_from_json(paths.read_paths().get('DATA'), paths.read_paths().get('RESPONSE_JSON'))
    Results.show_plotted_graph()


def display_history():
    all_dates = database.retrieve_dates()
    sidebar.show_sidebar()

    col2, col3 = st.columns(2)

    with col2:
        st.title("View Assessment History")
    with col3:
        Results.render_animation(paths.read_paths().get('DB_ANIMATION'), 250, 200)

    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; height: 150px;">            
    <h3>Select Date of assessment taken</h3>
    </div>
    """, unsafe_allow_html=True)

    selected_option = st.selectbox("", all_dates)

    # Submit button
    if st.button("Submit"):
        st.success(f"Selected option: {selected_option}")
        display_graph(selected_option)
