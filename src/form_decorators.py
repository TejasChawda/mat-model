import streamlit as st
import hydralit_components as hc
import time
from streamlit_lottie import st_lottie
import json


def loader():
    with open("/Users/admin/Desktop/pythonStreamlitDemo/Files/loader.json") as source:
        animation = json.load(source)

    st_lottie(animation)


def dynamic_progress_bar(current_form, total):
    progress_bar = st.empty()

    progress = current_form / total
    progress_percentage = int(progress * 100)

    progress_bar.progress(progress_percentage)
