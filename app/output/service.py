"""Public entry point for Phase 6 — this is what Phase 5's scheduler calls after each signal.

CSV logs every tick (full audit trail); Telegram only fires for an actual
BUY/SELL call, not HOLD — see README.
"""

from datetime import datetime, timezone
from typing import Optional

from app.config import load_config
from app.decision.models import TradeSignal
from app.output.csv_store import append_signal
from app.output.formatting import format_message
from app.output.telegram_notifier import send_message
from app.risk.models import RiskPlan


def record_signal(
    env_name: Optional[str],
    signal: TradeSignal,
    risk_plan: Optional[RiskPlan] = None,
    hold_duration: Optional[str] = None,
    balance_inr: Optional[float] = None,
) -> None:
    cfg = load_config(env_name)
    timestamp = datetime.now(timezone.utc).isoformat()

    append_signal(timestamp, signal, risk_plan=risk_plan)

    if signal.signal not in ("BUY", "SELL"):
        return  # only notify on an actual trade call, not HOLD

    bot_token = cfg["TELEGRAM_BOT_TOKEN"]
    chat_id = cfg["TELEGRAM_CHAT_ID"]
    if bot_token and chat_id:
        send_message(
            bot_token,
            chat_id,
            format_message(
                signal, cfg["SYMBOL"], risk_plan=risk_plan, hold_duration=hold_duration, balance_inr=balance_inr
            ),
        )
