"""Manual verification for Phase 8: python -m app.risk.check [env_name]

Uses real Phase 1/2 data with a synthetic BUY/SELL signal (no Claude call),
since Phase 4 is still blocked on API credits.
"""

import sys

from app.data.service import get_candles
from app.decision.models import TradeSignal
from app.patterns.engine import analyze
from app.risk.service import get_risk_plan


def main() -> None:
    env_name = sys.argv[1] if len(sys.argv) > 1 else None
    candles = get_candles(env_name, output_size=50)
    snapshot = analyze(candles)

    for direction in ["BUY", "SELL"]:
        signal = TradeSignal(signal=direction, confidence=70, reason="Phase 8 test")
        plan = get_risk_plan(env_name, signal, snapshot)
        print(f"[Phase 8] {direction}: {plan.to_dict()}")


if __name__ == "__main__":
    main()
