"""Public entry point for Phase 4 — combines Phase 2 + Phase 3 output, calls Claude.

This is what Phase 5 (scheduler) will call on each tick.
"""

from typing import Optional, Tuple

from app.config import load_config
from app.data.service import get_candles
from app.decision.claude_client import get_signal
from app.decision.models import TradeSignal
from app.decision.prompt import SYSTEM_PROMPT, build_user_prompt
from app.news.service import get_headlines
from app.patterns.engine import analyze
from app.patterns.models import MarketSnapshot


def get_trade_signal_with_snapshot(env_name: Optional[str] = None) -> Tuple[TradeSignal, MarketSnapshot]:
    """Like get_trade_signal, but also returns the MarketSnapshot — Phase 8 needs
    the entry price and ATR from it to compute stop-loss/take-profit."""
    cfg = load_config(env_name)
    api_key = cfg["ANTHROPIC_API_KEY"]
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set — add it to your .env file.")

    candles = get_candles(env_name, output_size=50)
    snapshot = analyze(candles)
    headlines = get_headlines(env_name)

    user_prompt = build_user_prompt(snapshot, headlines)
    result = get_signal(SYSTEM_PROMPT, user_prompt, api_key=api_key)

    signal = TradeSignal(
        signal=result["signal"],
        confidence=result["confidence"],
        reason=result["reason"],
    )
    return signal, snapshot


def get_trade_signal(env_name: Optional[str] = None) -> TradeSignal:
    signal, _snapshot = get_trade_signal_with_snapshot(env_name)
    return signal
