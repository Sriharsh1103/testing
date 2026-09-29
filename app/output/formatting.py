"""Formats a TradeSignal into a human-readable notification message."""

from app.decision.models import TradeSignal

EMOJI = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}


def format_message(signal: TradeSignal, symbol: str) -> str:
    emoji = EMOJI.get(signal.signal, "")
    return (
        f"{emoji} {signal.signal} — {symbol}\n"
        f"Confidence: {signal.confidence}%\n"
        f"Reason: {signal.reason}"
    )
