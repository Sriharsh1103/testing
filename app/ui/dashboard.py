import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.config import env_file_for  # noqa: E402
from app.constants import ENVS, PHASES, REQUIRED_KEYS, OPTIONAL_KEYS  # noqa: E402
from app.helpers import mask_secret  # noqa: E402

st.set_page_config(page_title="Gold Signal System — Setup", layout="centered")

st.title("Gold (XAU/USD) Signal System")
st.caption("Phase 0 — setup & environment check")

active_env = os.getenv("APP_ENV", "development")
st.info(f"Active environment (APP_ENV): **{active_env}**")

st.subheader("Environment key status")


def render_key_group(label: str, keys: list[str], values: dict, required: bool) -> None:
    st.markdown(f"**{label}**")
    for key in keys:
        val = values.get(key, "")
        if val:
            st.success(f"{key}: set ({mask_secret(val)})")
        elif required:
            st.warning(f"{key}: missing")
        else:
            st.caption(f"{key}: not set")


for env_name in ENVS:
    env_path = env_file_for(env_name)
    marker = " (active)" if env_name == active_env else ""
    with st.expander(f"{env_name}{marker} — {env_path.name}", expanded=(env_name == active_env)):
        if not env_path.exists():
            st.error(f"File not found: {env_path}")
            continue
        values = dotenv_values(env_path)
        render_key_group("Required", REQUIRED_KEYS, values, required=True)
        render_key_group("Optional", OPTIONAL_KEYS, values, required=False)

st.subheader("Roadmap")
for phase, desc, status in PHASES:
    icon = "✅" if status == "done" else "⬜"
    st.write(f"{icon} **{phase}** — {desc}")

st.divider()
st.caption("Fill missing keys in the matching .env.<environment> file, then rerun this dashboard.")
