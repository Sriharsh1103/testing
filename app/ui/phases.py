"""Phases page — status table for every phase: what it does, done/pending/on hold, blocked-on."""

import streamlit as st

from app.constants import PHASES

_STATUS_ICON = {"done": "✅", "pending": "⬜", "on hold": "⏸️"}


def render() -> None:
    st.subheader("Phase overview")
    rows = [
        {
            "Phase": phase,
            "What it does": desc,
            "Status": f"{_STATUS_ICON.get(status, '')} {status}",
            "Pending / blocked on": pending or "—",
        }
        for phase, desc, status, pending in PHASES
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
