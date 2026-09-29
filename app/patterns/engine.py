"""Phase 2 orchestrator — this is what Phase 4 (Claude layer) will import."""

from typing import List

from app.data.models import Candle
from app.patterns.candlestick import detect_pattern
from app.patterns.levels import find_support_resistance
from app.patterns.models import MarketSnapshot
from app.patterns.volatility import volatility_signal


def analyze(candles: List[Candle]) -> MarketSnapshot:
    if not candles:
        raise ValueError("analyze() requires at least one candle")

    levels = find_support_resistance(candles)

    return MarketSnapshot(
        last_close=candles[-1].close,
        support=levels["support"],
        resistance=levels["resistance"],
        pattern=detect_pattern(candles),
        volatility=volatility_signal(candles),
    )
