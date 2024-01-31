import streamlit as st
import options
import paths
import Session_state
import Results
import Update

state = Session_state.get_session_state()

data = Session_state.data

disable_button = False


def main():

    global disable_button

    st.title("Testing Assessment")

    st.write(state.available_scale_ids)

    st.markdown(
        """
        <style>
            .btn-container {
                position: absolute;
                top: 10px;
                left: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    button_mapping = {
        "END TEST": "Homepage",
        "SUBMIT": "Graph",
    }

    # Create buttons in a single row
    end = st.button("END TEST", key=1)
    submit = st.button("SUBMIT", key=2)

    # Check button clicks and update state accordingly
    if end:
        state.page = button_mapping["END TEST"]
        st.rerun()
    elif submit:
        state.page = button_mapping["SUBMIT"]
        st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        st.progress(state.progress)

    with col2:
        st.write(str(state.progress) + "%")

    st.write(state.level_id + " - " + state.scale_id)

    form = st.form(key='questionnaire_form')
    filtered_questions = data[
        (data["Scale_Id"] == state.scale_id) & (data["Level_Id"] == state.level_id)]

    if filtered_questions.empty:
        st.warning("No questions found for the provided Scale ID and Level ID.")
        Update.update_level_id()
    elif state.available_scale_ids is None:
        disable_button = True
    else:
        for _, question in filtered_questions.iterrows():
            widget_key = f"{question['Q_Id']}_{state.level_id}"  # Use both Q_Id and level_id as a key
            option = form.radio(question["Questions"], list(choice.name for choice in options.Options), key=widget_key)

            # if option is not None:
            selected_option = options.Options[option] if option else None
            option_values = selected_option.value if selected_option else None

            # Store the response for each question with Question_ID
            state.responses[widget_key] = {
                "Question_Id": question['Q_Id'],
                "Value": option_values,
                "Level_Id": state.level_id,
                "Scale": state.scale_id
            }

        # Outside the for loop
        if form.form_submit_button("Submit Responses", disabled=disable_button):
            try:
                if len(state.responses) == len(filtered_questions):
                    # if not state.available_scale_ids:
                    #     state.page = "Graph"
                    #     st.rerun()

                    Results.spinner("submitting your responses....", 2)

                    # accuracy = Results.calculate_accuracy()
                    # st.success(f"Responses submitted successfully! Accuracy: {accuracy:.2f}%")

                    # Save responses to a JSON file
                    json_file_path = paths.read_paths().get('RESPONSE_JSON')
                    Results.save_responses_to_json(list(state.responses.values()), json_file_path)
                    Update.update_csv_from_json(paths.read_paths().get('DATA'), json_file_path)

                    Update.update_level_id()
                    st.write(f"Updated Level: {state.level_id}")
            except Exception as e:
                st.warning("Please answer all the questions before submitting....")
                print(e)
