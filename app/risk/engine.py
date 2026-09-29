"""Phase 8 — derives stop-loss/take-profit from ATR (Phase 2) and the trade direction.

No account size is used, by design (see README) — this reports the %-risk to
take on the trade, not an exact lot size. Pure function, no I/O.
"""

from typing import Optional

from app.decision.models import TradeSignal
from app.patterns.models import MarketSnapshot
from app.risk.models import RiskPlan


def compute_risk_plan(
    signal: TradeSignal,
    snapshot: MarketSnapshot,
    risk_percent: float,
    atr_stop_multiplier: float,
    reward_risk_ratio: float,
) -> Optional[RiskPlan]:
    if signal.signal not in ("BUY", "SELL"):
        return None

    entry = snapshot.last_close
    stop_distance = atr_stop_multiplier * snapshot.volatility.atr
    reward_distance = stop_distance * reward_risk_ratio

    if signal.signal == "BUY":
        stop_loss = entry - stop_distance
        take_profit = entry + reward_distance
    else:  # SELL
        stop_loss = entry + stop_distance
        take_profit = entry - reward_distance

    return RiskPlan(
        entry=round(entry, 4),
        stop_loss=round(stop_loss, 4),
        take_profit=round(take_profit, 4),
        risk_percent=risk_percent,
        reward_risk_ratio=reward_risk_ratio,
    )
