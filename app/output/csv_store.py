"""Appends trade signals (+ optional Phase 8 risk plan) to a local CSV log."""

import csv
from pathlib import Path
from typing import Optional

from app.decision.models import TradeSignal
from app.risk.models import RiskPlan

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PATH = ROOT / "data" / "signals.csv"

FIELDNAMES = [
    "timestamp",
    "signal",
    "confidence",
    "reason",
    "entry",
    "stop_loss",
    "take_profit",
    "risk_percent",
    "reward_risk_ratio",
]


def append_signal(
    timestamp: str,
    signal: TradeSignal,
    risk_plan: Optional[RiskPlan] = None,
    path: Path = DEFAULT_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()

    row = {"timestamp": timestamp, **signal.to_dict()}
    if risk_plan:
        row.update(risk_plan.to_dict())

    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if is_new:
            writer.writeheader()
        writer.writerow(row)
