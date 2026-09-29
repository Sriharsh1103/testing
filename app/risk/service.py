"""Public entry point for Phase 8 — this is what Phase 5's scheduler calls after each signal."""

from typing import Optional

from app.config import load_config
from app.decision.models import TradeSignal
from app.patterns.models import MarketSnapshot
from app.risk.engine import compute_risk_plan
from app.risk.models import RiskPlan


def get_risk_plan(
    env_name: Optional[str], signal: TradeSignal, snapshot: MarketSnapshot
) -> Optional[RiskPlan]:
    cfg = load_config(env_name)
    return compute_risk_plan(
        signal=signal,
        snapshot=snapshot,
        risk_percent=cfg["RISK_PER_TRADE_PCT"],
        atr_stop_multiplier=cfg["ATR_STOP_MULTIPLIER"],
        reward_risk_ratio=cfg["REWARD_RISK_RATIO"],
    )
