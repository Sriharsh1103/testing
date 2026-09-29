"""Phase 5 — runs Phase 1-4 on a loop, Phase 8 (risk plan) + Phase 6 (log + notify)
after each signal.

Usage:
  python -m app.scheduler.runner [env_name]           # loop forever
  python -m app.scheduler.runner [env_name] --once     # single tick, for testing
"""

import sys
import time
from datetime import datetime, timezone

from app.config import load_config
from app.decision.service import get_trade_signal_with_snapshot
from app.output.service import record_signal
from app.risk.service import get_risk_plan
from app.scheduler.session import is_active_session


def run_once(env_name: str = None) -> None:
    now = datetime.now(timezone.utc).isoformat()
    try:
        signal, snapshot = get_trade_signal_with_snapshot(env_name)
        risk_plan = get_risk_plan(env_name, signal, snapshot)
        record_signal(env_name, signal, risk_plan=risk_plan)
        print(f"[{now}] {signal.signal} (confidence {signal.confidence}) — {signal.reason}")
        if risk_plan:
            print(f"  entry {risk_plan.entry} | SL {risk_plan.stop_loss} | TP {risk_plan.take_profit}")
    except Exception as exc:  # noqa: BLE001 — one bad tick must not kill the loop
        print(f"[{now}] ERROR: {exc}")


def run_forever(env_name: str = None) -> None:
    cfg = load_config(env_name)
    active_min = cfg["POLL_INTERVAL_ACTIVE_MIN"]
    idle_min = cfg["POLL_INTERVAL_IDLE_MIN"]

    print(
        f"[Phase 5] Scheduler started — env={cfg['ENV']} "
        f"(active session: every {active_min}min, idle: every {idle_min}min)"
    )

    while True:
        run_once(env_name)
        interval_min = active_min if is_active_session() else idle_min
        print(f"  next tick in {interval_min} min")
        time.sleep(interval_min * 60)


def main() -> None:
    args = sys.argv[1:]
    once = "--once" in args
    env_name = next((a for a in args if not a.startswith("--")), None)

    run_once(env_name) if once else run_forever(env_name)


if __name__ == "__main__":
    main()
