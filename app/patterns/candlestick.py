"""Candlestick pattern detection — pure functions over Candle data, no I/O."""

from typing import List, Optional

from app.data.models import Candle
from app.patterns.models import PatternSignal

DOJI_BODY_RATIO = 0.1
WICK_TO_BODY_RATIO = 2


def _body(c: Candle) -> float:
    return abs(c.close - c.open)


def _range(c: Candle) -> float:
    return c.high - c.low


def _upper_wick(c: Candle) -> float:
    return c.high - max(c.close, c.open)


def _lower_wick(c: Candle) -> float:
    return min(c.close, c.open) - c.low


def _is_bullish(c: Candle) -> bool:
    return c.close > c.open


def _is_doji(c: Candle) -> bool:
    rng = _range(c)
    return rng > 0 and (_body(c) / rng) <= DOJI_BODY_RATIO


def _is_hammer(c: Candle) -> bool:
    body = _body(c)
    if body == 0:
        return False
    return _lower_wick(c) >= WICK_TO_BODY_RATIO * body and _upper_wick(c) <= body


def _is_shooting_star(c: Candle) -> bool:
    body = _body(c)
    if body == 0:
        return False
    return _upper_wick(c) >= WICK_TO_BODY_RATIO * body and _lower_wick(c) <= body


def _is_bullish_engulfing(prev: Candle, curr: Candle) -> bool:
    return (
        not _is_bullish(prev)
        and _is_bullish(curr)
        and curr.open <= prev.close
        and curr.close >= prev.open
    )


def _is_bearish_engulfing(prev: Candle, curr: Candle) -> bool:
    return (
        _is_bullish(prev)
        and not _is_bullish(curr)
        and curr.open >= prev.close
        and curr.close <= prev.open
    )


def detect_pattern(candles: List[Candle]) -> Optional[PatternSignal]:
    """Check the last 1-2 candles and return the strongest pattern found, if any.

    Checked in priority order: engulfing (needs 2 candles) before single-candle
    patterns, since engulfing is the stronger reversal signal.
    """
    if len(candles) < 2:
        return None

    prev, curr = candles[-2], candles[-1]

    if _is_bullish_engulfing(prev, curr):
        return PatternSignal(name="bullish_engulfing", bias="bullish")
    if _is_bearish_engulfing(prev, curr):
        return PatternSignal(name="bearish_engulfing", bias="bearish")
    if _is_hammer(curr):
        return PatternSignal(name="hammer", bias="bullish")
    if _is_shooting_star(curr):
        return PatternSignal(name="shooting_star", bias="bearish")
    if _is_doji(curr):
        return PatternSignal(name="doji", bias="neutral")

    return None
