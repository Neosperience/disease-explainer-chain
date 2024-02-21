from pathlib import Path

import streamlit as st

DEFAULT_LOGO_URL = "https://www.neosperience.com/wp-content/themes/neos/images/logo.png"

def show_card(filename: str = "./card.md") -> None:
    st.write(Path(filename).read_text())

LOGO_HTML = """<img src="{uri}" width="{width}px" style="margin-left:{margin_left}px"/>"""

def show_logo(logo_url: str = DEFAULT_LOGO_URL, width: int = 200) -> None:
    html = LOGO_HTML.format(uri=logo_url, width=width, margin_left=-(width/20))
    st.markdown(html, unsafe_allow_html=True)
