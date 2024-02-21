import os
import logging

import streamlit as st

def load_env() -> None:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    logging.basicConfig(level=logging.INFO)