"""Cached wrappers used only by the Home page.

An auto-refreshing UI reruns the whole script often — these TTLs make sure that
only re-renders from cache, not real API/Claude calls, happen on every rerun.
Candle/news TTLs stay well inside the free-tier daily quotas even if the
dashboard is left open all day; the Claude call is cached longest since it's
the one that costs money (matches the project's "minimum token use" goal).
"""

import streamlit as st

from app.data.service import get_candles as _get_candles
from app.decision.service import get_trade_signal_with_snapshot as _get_trade_signal_with_snapshot
from app.news.service import get_headlines as _get_headlines

CANDLES_TTL = 300  # 5 min
NEWS_TTL = 600  # 10 min
SIGNAL_TTL = 900  # 15 min — matches the default active-session poll interval


@st.cache_data(ttl=CANDLES_TTL, show_spinner=False)
def get_candles(env_name: str, output_size: int):
    return _get_candles(env_name, output_size=output_size)


@st.cache_data(ttl=NEWS_TTL, show_spinner=False)
def get_headlines(env_name: str):
    return _get_headlines(env_name)


@st.cache_data(ttl=SIGNAL_TTL, show_spinner=False)
def get_trade_signal_with_snapshot(env_name: str):
    return _get_trade_signal_with_snapshot(env_name)
