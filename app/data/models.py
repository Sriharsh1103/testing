"""Shared data shape for Phase 1 onwards — Phase 2 (patterns) consumes this directly."""

from dataclasses import dataclass


@dataclass
class Candle:
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_dict(self) -> dict:
        return {
            "datetime": self.datetime,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }
