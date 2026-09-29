"""Manual verification for the paper ledger: python -m app.paper.check [env_name]

Simulates one open (BUY) and one close-by-take-profit, with synthetic data —
no Claude call needed.
"""

import sys

from app.data.models import Candle
from app.decision.models import TradeSignal
from app.paper.service import update_ledger
from app.risk.models import RiskPlan


def main() -> None:
    env_name = sys.argv[1] if len(sys.argv) > 1 else None

    signal = TradeSignal(signal="BUY", confidence=80, reason="Paper ledger test")
    plan = RiskPlan(entry=100.0, stop_loss=98.0, take_profit=103.0, risk_percent=1.0, reward_risk_ratio=1.5)
    flat_candle = Candle(datetime="t0", open=100, high=100.5, low=99.5, close=100, volume=0)

    state, outcome = update_ledger(env_name, signal, plan, flat_candle)
    print(f"[Paper] after open attempt: balance={state.balance} position={state.position} outcome={outcome}")

    tp_candle = Candle(datetime="t1", open=101, high=103.5, low=100.5, close=103, volume=0)
    state, outcome = update_ledger(env_name, signal, plan, tp_candle)
    print(f"[Paper] after TP candle: balance={state.balance} position={state.position} outcome={outcome}")


if __name__ == "__main__":
    main()
