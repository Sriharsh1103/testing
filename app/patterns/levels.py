"""Support/resistance detection — pure functions over Candle data, no I/O."""

from typing import List

from app.data.models import Candle

DEFAULT_LOOKBACK = 20


def find_support_resistance(candles: List[Candle], lookback: int = DEFAULT_LOOKBACK) -> dict:
    """Recent swing low/high over the lookback window — simple, standard S/R baseline."""
    window = candles[-lookback:] if len(candles) >= lookback else candles
    return {
        "support": min(c.low for c in window),
        "resistance": max(c.high for c in window),
    }
