"""Manual verification for Phase 6: python -m app.output.check [env_name] [--send-telegram]

By default this only writes a test row to the CSV log (safe, local, no external
effect). Pass --send-telegram to also send a real message to your configured
Telegram chat — only do that when you actually want to confirm delivery.
"""

import sys
from datetime import datetime, timezone

from app.config import load_config
from app.decision.models import TradeSignal
from app.output.csv_store import append_signal
from app.output.formatting import format_message
from app.output.telegram_notifier import send_message


def main() -> None:
    args = sys.argv[1:]
    send_telegram = "--send-telegram" in args
    env_name = next((a for a in args if not a.startswith("--")), None)

    cfg = load_config(env_name)
    signal = TradeSignal(signal="HOLD", confidence=50, reason="Phase 6 test signal — not a real trade call.")
    timestamp = datetime.now(timezone.utc).isoformat()

    append_signal(timestamp, signal)
    print(f"[Phase 6] Logged test signal to CSV at {timestamp}")

    if not send_telegram:
        print("[Phase 6] Skipped Telegram send (pass --send-telegram to test delivery)")
        return

    bot_token = cfg["TELEGRAM_BOT_TOKEN"]
    chat_id = cfg["TELEGRAM_CHAT_ID"]
    if not bot_token or not chat_id:
        print("[Phase 6] Telegram not configured — skipping")
        return

    send_message(bot_token, chat_id, format_message(signal, cfg["SYMBOL"]))
    print("[Phase 6] Sent test message to Telegram")


if __name__ == "__main__":
    main()
