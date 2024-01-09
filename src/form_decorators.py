import time
import streamlit as st


def loader(message):
    with st.spinner(message):
        time.sleep(2)


def dynamic_progress_bar(current_form, total):
    progress_bar = st.empty()

    progress = current_form / total
    progress_percentage = int(progress * 100)

    progress_bar.progress(progress_percentage)
