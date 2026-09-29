"""Volatility-based volume proxy (ATR) — pure functions over Candle data, no I/O.

XAU/USD has no real volume (OTC market). This ratio — latest candle's true range
vs the recent average — is the stand-in "activity" signal: well above 1 behaves
like a volume spike, well below 1 behaves like a quiet/low-activity market.
"""

from typing import List

from app.data.models import Candle
from app.patterns.models import VolatilitySignal

DEFAULT_ATR_PERIOD = 14
HIGH_ACTIVITY_RATIO = 1.5
LOW_ACTIVITY_RATIO = 0.7


def _true_range(current: Candle, previous: Candle) -> float:
    return max(
        current.high - current.low,
        abs(current.high - previous.close),
        abs(current.low - previous.close),
    )


def _average_true_range(candles: List[Candle], period: int) -> float:
    trs = [_true_range(candles[i], candles[i - 1]) for i in range(1, len(candles))]
    recent = trs[-period:]
    return sum(recent) / len(recent) if recent else 0.0


def volatility_signal(candles: List[Candle], period: int = DEFAULT_ATR_PERIOD) -> VolatilitySignal:
    if len(candles) < 2:
        return VolatilitySignal(atr=0.0, last_true_range=0.0, ratio=0.0, label="unknown")

    atr = _average_true_range(candles, period)
    last_tr = _true_range(candles[-1], candles[-2])
    ratio = round(last_tr / atr, 2) if atr > 0 else 0.0

    if ratio >= HIGH_ACTIVITY_RATIO:
        label = "high"
    elif ratio <= LOW_ACTIVITY_RATIO:
        label = "low"
    else:
        label = "normal"

    return VolatilitySignal(atr=atr, last_true_range=last_tr, ratio=ratio, label=label)
