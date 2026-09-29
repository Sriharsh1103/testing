"""Manual verification for Phase 4: python -m app.decision.check [env_name]"""

import sys

from app.decision.service import get_trade_signal


def main() -> None:
    env_name = sys.argv[1] if len(sys.argv) > 1 else None
    signal = get_trade_signal(env_name)

    print(f"[Phase 4] Signal: {signal.signal} (confidence: {signal.confidence})")
    print(f"  Reason: {signal.reason}")


if __name__ == "__main__":
    main()
