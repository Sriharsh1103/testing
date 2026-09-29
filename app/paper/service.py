"""Public entry point for the paper-trading ledger — called each scheduler tick.

This is the only place that should mutate the ledger (see README: the Home
dashboard only reads it, so an auto-refreshing UI never double-opens/closes
positions or double-sends the close notification). Every closed trade also
gets appended to the trade journal (journal.py) — the "learning data".
"""

from datetime import datetime, timezone
from typing import Optional, Tuple

from app.config import load_config
from app.data.models import Candle
from app.decision.models import TradeSignal
from app.paper import journal, storage
from app.paper.ledger import check_close, open_position
from app.paper.models import LedgerState
from app.patterns.models import MarketSnapshot
from app.risk.models import RiskPlan


def update_ledger(
    env_name: Optional[str],
    signal: TradeSignal,
    plan: Optional[RiskPlan],
    snapshot: MarketSnapshot,
    latest_candle: Candle,
) -> Tuple[LedgerState, Optional[str]]:
    cfg = load_config(env_name)
    env_key = env_name or cfg["ENV"]
    state = storage.load(env_key, cfg["PAPER_INITIAL_BALANCE"])
    now = datetime.now(timezone.utc).isoformat()

    outcome = None
    if state.position is not None:
        closing_position = state.position
        state, outcome = check_close(state, latest_candle)
        if outcome:
            journal.append_trade(now, closing_position, outcome, state.balance)
    elif plan is not None:
        pattern_name = snapshot.pattern.name if snapshot.pattern else None
        state = open_position(state, signal, plan, now, pattern_name=pattern_name)

    storage.save(env_key, state)
    return state, outcome
