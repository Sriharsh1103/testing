"""Shared data shape for Phase 2 — Phase 4 (Claude layer) consumes MarketSnapshot.to_dict()."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PatternSignal:
    name: str
    bias: str  # "bullish" | "bearish" | "neutral"


@dataclass
class VolatilitySignal:
    atr: float
    last_true_range: float
    ratio: float
    label: str  # "high" | "normal" | "low" | "unknown"


@dataclass
class MarketSnapshot:
    last_close: float
    support: float
    resistance: float
    pattern: Optional[PatternSignal]
    volatility: VolatilitySignal

    def to_dict(self) -> dict:
        return {
            "last_close": self.last_close,
            "support": self.support,
            "resistance": self.resistance,
            "pattern": {"name": self.pattern.name, "bias": self.pattern.bias} if self.pattern else None,
            "volatility": {
                "atr": round(self.volatility.atr, 4),
                "ratio": self.volatility.ratio,
                "label": self.volatility.label,
            },
        }
