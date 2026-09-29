"""Formats a TradeSignal (+ optional Phase 8 risk plan) into a notification message.

Price levels (entry/SL/TP) stay in USD — that's how gold (XAU/USD) trades.
The account balance and risk/reward amounts are shown in INR (₹) since that's
the currency the paper-trading balance is entered in.
"""

from typing import Optional

from app.decision.models import TradeSignal
from app.risk.models import RiskPlan

EMOJI = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}


def format_message(
    signal: TradeSignal,
    symbol: str,
    risk_plan: Optional[RiskPlan] = None,
    hold_duration: Optional[str] = None,
    balance_inr: Optional[float] = None,
) -> str:
    emoji = EMOJI.get(signal.signal, "")
    lines = [
        f"{emoji} {signal.signal} — {symbol}",
        f"Confidence: {signal.confidence}%",
        f"Reason: {signal.reason}",
    ]
    if risk_plan:
        lines += [
            f"Entry: {risk_plan.entry} USD",
            f"Stop-loss: {risk_plan.stop_loss} USD",
            f"Take-profit: {risk_plan.take_profit} USD",
        ]
        if balance_inr is not None:
            risk_amount = round(balance_inr * risk_plan.risk_percent / 100, 2)
            reward_amount = round(risk_amount * risk_plan.reward_risk_ratio, 2)
            lines.append(
                f"Risk: ₹{risk_amount} of ₹{round(balance_inr, 2)} "
                f"({risk_plan.risk_percent}%) | Potential: ₹{reward_amount}"
            )
        else:
            lines.append(
                f"Risk: {risk_plan.risk_percent}% of capital (risk:reward 1:{risk_plan.reward_risk_ratio})"
            )
    if hold_duration:
        lines.append(f"Suggested hold time: {hold_duration}")
    return "\n".join(lines)


def format_close_message(outcome: str, balance_inr: float, symbol: str) -> str:
    emoji = "✅" if outcome == "TP" else "❌"
    return f"{emoji} Paper position closed ({outcome}) — {symbol}\nNew paper balance: ₹{round(balance_inr, 2)}"
