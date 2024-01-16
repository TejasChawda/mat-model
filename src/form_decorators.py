import streamlit as st
import hydralit_components as hc
import time
import json


def loader(message):
    with hc.HyLoader(message,hc.Loaders.standard_loaders,index=[2]):
        time.sleep(2)



def dynamic_progress_bar(current_form, total):
    progress_bar = st.empty()

    progress = current_form / total
    progress_percentage = int(progress * 100)

    progress_bar.progress(progress_percentage)
