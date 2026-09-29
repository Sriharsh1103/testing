"""Phase 5 — runs Phase 1-4 on a loop. Output/storage is Phase 6's job; this just
prints each tick so it's useful stand-alone in the meantime.

Usage:
  python -m app.scheduler.runner [env_name]           # loop forever
  python -m app.scheduler.runner [env_name] --once     # single tick, for testing
"""

import sys
import time
from datetime import datetime, timezone

from app.config import load_config
from app.decision.service import get_trade_signal
from app.scheduler.session import is_active_session


def run_once(env_name: str = None) -> None:
    now = datetime.now(timezone.utc).isoformat()
    try:
        signal = get_trade_signal(env_name)
        print(f"[{now}] {signal.signal} (confidence {signal.confidence}) — {signal.reason}")
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
