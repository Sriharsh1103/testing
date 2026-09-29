"""Environment page — view masked key status, or edit values (writes to .env.<environment>)."""

import streamlit as st
from dotenv import dotenv_values, set_key

from app.config import env_file_for
from app.constants import ENVS, OPTIONAL_KEYS, REQUIRED_KEYS
from app.helpers import mask_secret


def _render_key_group(label: str, keys: list[str], values: dict, required: bool) -> None:
    st.markdown(f"**{label}**")
    for key in keys:
        val = values.get(key, "")
        if val:
            st.success(f"{key}: set ({mask_secret(val)})")
        elif required:
            st.warning(f"{key}: missing")
        else:
            st.caption(f"{key}: not set")


def render(active_env: str) -> None:
    st.subheader("Environment")
    tab_view, tab_secrets = st.tabs(["View", "Secrets (edit)"])

    with tab_view:
        for env_name in ENVS:
            env_path = env_file_for(env_name)
            marker = " (active)" if env_name == active_env else ""
            with st.expander(f"{env_name}{marker} — {env_path.name}", expanded=(env_name == active_env)):
                if not env_path.exists():
                    st.error(f"File not found: {env_path}")
                    continue
                values = dotenv_values(env_path)
                _render_key_group("Required", REQUIRED_KEYS, values, required=True)
                _render_key_group("Optional", OPTIONAL_KEYS, values, required=False)

    with tab_secrets:
        st.caption("Edit values and Save — writes straight to the .env.<environment> file on disk.")
        edit_env = st.selectbox("Environment to edit", ENVS, index=ENVS.index(active_env))
        edit_path = env_file_for(edit_env)
        current_values = dotenv_values(edit_path) if edit_path.exists() else {}

        with st.form("secrets_form"):
            new_values = {}
            st.markdown("**Required**")
            for key in REQUIRED_KEYS:
                new_values[key] = st.text_input(key, value=current_values.get(key, ""), type="password")
            st.markdown("**Optional**")
            for key in OPTIONAL_KEYS:
                new_values[key] = st.text_input(key, value=current_values.get(key, ""), type="password")
            saved = st.form_submit_button("Save")

        if saved:
            for key, val in new_values.items():
                set_key(str(edit_path), key, val)
            st.success(f"Saved to {edit_path.name}. Switch to Home to use the new values.")
