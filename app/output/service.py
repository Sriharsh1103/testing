"""Public entry point for Phase 6 — this is what Phase 5's scheduler calls after each signal."""

from datetime import datetime, timezone
from typing import Optional

from app.config import load_config
from app.decision.models import TradeSignal
from app.output.csv_store import append_signal
from app.output.formatting import format_message
from app.output.telegram_notifier import send_message


def record_signal(env_name: Optional[str], signal: TradeSignal) -> None:
    cfg = load_config(env_name)
    timestamp = datetime.now(timezone.utc).isoformat()

    append_signal(timestamp, signal)

    bot_token = cfg["TELEGRAM_BOT_TOKEN"]
    chat_id = cfg["TELEGRAM_CHAT_ID"]
    if bot_token and chat_id:
        send_message(bot_token, chat_id, format_message(signal, cfg["SYMBOL"]))
