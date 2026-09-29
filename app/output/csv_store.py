"""Appends trade signals to a local CSV log — the persistent record of every signal."""

import csv
from pathlib import Path

from app.decision.models import TradeSignal

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PATH = ROOT / "data" / "signals.csv"

FIELDNAMES = ["timestamp", "signal", "confidence", "reason"]


def append_signal(timestamp: str, signal: TradeSignal, path: Path = DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()

    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if is_new:
            writer.writeheader()
        writer.writerow({"timestamp": timestamp, **signal.to_dict()})
