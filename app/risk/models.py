"""Shared data shape for Phase 8 — this is what Phase 6 (output) logs alongside the signal."""

from dataclasses import dataclass


@dataclass
class RiskPlan:
    entry: float
    stop_loss: float
    take_profit: float
    risk_percent: float  # % of capital to risk on this trade
    reward_risk_ratio: float

    def to_dict(self) -> dict:
        return {
            "entry": self.entry,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "risk_percent": self.risk_percent,
            "reward_risk_ratio": self.reward_risk_ratio,
        }
