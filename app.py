import streamlit as st

from app.st_auth import check_password # type: ignore
from app.st_nsp import show_logo # type: ignore
from app import app_name, app_executable # type: ignore

#if not check_password():
#    st.stop()

# st.set_page_config(page_title=app_name, page_icon=":robot:")

show_logo()

app_executable()
