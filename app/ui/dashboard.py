"""Entrypoint only — sidebar navigation, delegates rendering to home/environment/phases."""

import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.ui import environment, home, phases  # noqa: E402

st.set_page_config(page_title="Gold Signal System", layout="centered")

active_env = os.getenv("APP_ENV", "development")

st.sidebar.title("Gold (XAU/USD) Signal System")
st.sidebar.caption(f"Environment: **{active_env}**")
page = st.sidebar.radio("Navigate", ["Home", "Environment", "Phases"])

if page == "Home":
    home.render(active_env)
elif page == "Environment":
    environment.render(active_env)
else:
    phases.render()
