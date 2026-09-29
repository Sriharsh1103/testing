"""Builds the compact prompt sent to Claude — the main token-cost lever in the app.

Only a JSON summary of the snapshot + a handful of headlines go in, never raw
candle history or full articles, to keep each call small.
"""

import json
from typing import List

from app.news.models import NewsItem
from app.patterns.models import MarketSnapshot

SYSTEM_PROMPT = (
    "You are a trading-signal assistant for XAU/USD (gold). You are given a market "
    "snapshot (last close, support/resistance, a detected candlestick pattern, and "
    "a volatility ratio used as a proxy for volume/activity since gold has no "
    "centralized exchange volume) and a few recent relevant news headlines. "
    "Decide BUY, SELL, or HOLD with a confidence (0-100) and a one-sentence reason. "
    "This is a decision-support signal only — not guaranteed, not financial advice."
)


def build_user_prompt(snapshot: MarketSnapshot, headlines: List[NewsItem]) -> str:
    snapshot_json = json.dumps(snapshot.to_dict(), separators=(",", ":"))
    headline_lines = "\n".join(f"- {h.headline}" for h in headlines) or "(none)"
    return f"Market snapshot: {snapshot_json}\n\nRecent headlines:\n{headline_lines}"
