"""Phase 5 — runs Phase 1-4 on a loop; Phase 8 (risk plan) + Phase 6 (log + notify)
+ the paper-trading ledger after each signal.

Telegram only fires on an actual BUY/SELL call (not HOLD) — see README.
This is the only process that should touch the paper ledger or send signal/close
Telegram messages — the Home dashboard only reads/displays, never writes, so an
auto-refreshing browser tab can never double-fire a trade or a message.

Usage:
  python -m app.scheduler.runner [env_name]           # loop forever
  python -m app.scheduler.runner [env_name] --once     # single tick, for testing
"""

import sys
import time
from datetime import datetime, timezone

from app.config import load_config
from app.constants import HOLD_DURATION_HINT
from app.decision.service import get_trade_signal_with_snapshot
from app.output.formatting import format_close_message
from app.output.service import record_signal
from app.output.telegram_notifier import send_message
from app.paper import storage as paper_storage
from app.paper.service import update_ledger
from app.risk.service import get_risk_plan
from app.scheduler.session import is_active_session


def run_once(env_name: str = None) -> None:
    now = datetime.now(timezone.utc).isoformat()
    try:
        signal, snapshot, last_candle = get_trade_signal_with_snapshot(env_name)
        cfg = load_config(env_name)
        risk_plan = get_risk_plan(env_name, signal, snapshot)

        # balance *before* this tick's position (if any) opens — what the
        # Telegram message should quote as "risking X of Y"
        current_state = paper_storage.load(cfg["ENV"], cfg["PAPER_INITIAL_BALANCE"])
        hold_duration = HOLD_DURATION_HINT.get(cfg["TRADE_STYLE"])

        record_signal(
            env_name,
            signal,
            risk_plan=risk_plan,
            hold_duration=hold_duration,
            balance_inr=current_state.balance,
        )
        print(f"[{now}] {signal.signal} (confidence {signal.confidence}) — {signal.reason}")
        if risk_plan:
            print(f"  entry {risk_plan.entry} | SL {risk_plan.stop_loss} | TP {risk_plan.take_profit}")

        ledger_state, outcome = update_ledger(env_name, signal, risk_plan, snapshot, last_candle)
        if outcome:
            print(f"  paper trade closed: {outcome} -> balance {ledger_state.balance:.2f}")
            bot_token, chat_id = cfg["TELEGRAM_BOT_TOKEN"], cfg["TELEGRAM_CHAT_ID"]
            if bot_token and chat_id:
                send_message(
                    bot_token, chat_id, format_close_message(outcome, ledger_state.balance, cfg["SYMBOL"])
                )
    except Exception as exc:  # noqa: BLE001 — one bad tick must not kill the loop
        print(f"[{now}] ERROR: {exc}")


def run_forever(env_name: str = None) -> None:
    cfg = load_config(env_name)
    active_min = cfg["POLL_INTERVAL_ACTIVE_MIN"]
    idle_min = cfg["POLL_INTERVAL_IDLE_MIN"]

    print(
        f"[Phase 5] Scheduler started — env={cfg['ENV']} "
        f"(checks every {active_min}min active / {idle_min}min idle; "
        f"Telegram only fires on an actual BUY/SELL call)"
    )

    while True:
        run_once(env_name)
        # re-read config each tick so changes saved from the UI (trade style,
        # poll interval, etc.) take effect on the next iteration automatically
        cfg = load_config(env_name)
        active_min = cfg["POLL_INTERVAL_ACTIVE_MIN"]
        idle_min = cfg["POLL_INTERVAL_IDLE_MIN"]
        interval_min = active_min if is_active_session() else idle_min
        print(f"  next check in {interval_min} min")
        time.sleep(interval_min * 60)


def main() -> None:
    args = sys.argv[1:]
    once = "--once" in args
    env_name = next((a for a in args if not a.startswith("--")), None)

    run_once(env_name) if once else run_forever(env_name)


if __name__ == "__main__":
    main()
