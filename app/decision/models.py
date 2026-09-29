"""Shared data shape for Phase 4 — this is what Phase 5/6 consume."""

from dataclasses import dataclass


@dataclass
class TradeSignal:
    signal: str  # "BUY" | "SELL" | "HOLD"
    confidence: int  # 0-100
    reason: str

    def to_dict(self) -> dict:
        return {"signal": self.signal, "confidence": self.confidence, "reason": self.reason}
