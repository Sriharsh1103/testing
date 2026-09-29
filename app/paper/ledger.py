"""Paper-trading ledger logic — pure functions, no I/O.

Simulates P&L in %-of-capital terms using Phase 8's risk plan: at most one open
position at a time; a position closes when a later candle's high/low touches
its stop-loss or take-profit. If both are touched in the same candle, the
stop-loss is assumed to have hit first (the conservative/worse outcome).
"""

from typing import Optional, Tuple

from app.data.models import Candle
from app.decision.models import TradeSignal
from app.paper.models import LedgerState, Position
from app.risk.models import RiskPlan


def open_position(
    state: LedgerState,
    signal: TradeSignal,
    plan: RiskPlan,
    timestamp: str,
    pattern_name: Optional[str] = None,
) -> LedgerState:
    if state.position is not None or signal.signal not in ("BUY", "SELL"):
        return state

    position = Position(
        direction=signal.signal,
        entry=plan.entry,
        stop_loss=plan.stop_loss,
        take_profit=plan.take_profit,
        balance_at_open=state.balance,
        risk_percent=plan.risk_percent,
        reward_risk_ratio=plan.reward_risk_ratio,
        opened_at=timestamp,
        pattern_name=pattern_name,
        confidence=signal.confidence,
    )
    return LedgerState(
        balance=state.balance, position=position, trade_count=state.trade_count, win_count=state.win_count
    )


def check_close(state: LedgerState, candle: Candle) -> Tuple[LedgerState, Optional[str]]:
    """Returns (new_state, outcome) — outcome is "TP", "SL", or None if still open."""
    pos = state.position
    if pos is None:
        return state, None

    hit_sl = (pos.direction == "BUY" and candle.low <= pos.stop_loss) or (
        pos.direction == "SELL" and candle.high >= pos.stop_loss
    )
    hit_tp = (pos.direction == "BUY" and candle.high >= pos.take_profit) or (
        pos.direction == "SELL" and candle.low <= pos.take_profit
    )

    if not hit_sl and not hit_tp:
        return state, None

    outcome = "SL" if hit_sl else "TP"
    risk_amount = pos.balance_at_open * (pos.risk_percent / 100)
    delta = -risk_amount if outcome == "SL" else risk_amount * pos.reward_risk_ratio
    new_state = LedgerState(
        balance=state.balance + delta,
        position=None,
        trade_count=state.trade_count + 1,
        win_count=state.win_count + (1 if outcome == "TP" else 0),
    )
    return new_state, outcome
