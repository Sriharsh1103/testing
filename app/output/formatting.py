"""Formats a TradeSignal (+ optional Phase 8 risk plan) into a notification message."""

from typing import Optional

from app.decision.models import TradeSignal
from app.risk.models import RiskPlan

EMOJI = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}


def format_message(signal: TradeSignal, symbol: str, risk_plan: Optional[RiskPlan] = None) -> str:
    emoji = EMOJI.get(signal.signal, "")
    lines = [
        f"{emoji} {signal.signal} — {symbol}",
        f"Confidence: {signal.confidence}%",
        f"Reason: {signal.reason}",
    ]
    if risk_plan:
        lines += [
            f"Entry: {risk_plan.entry}",
            f"Stop-loss: {risk_plan.stop_loss}",
            f"Take-profit: {risk_plan.take_profit}",
            f"Risk: {risk_plan.risk_percent}% of capital (risk:reward 1:{risk_plan.reward_risk_ratio})",
        ]
    return "\n".join(lines)
