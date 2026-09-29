"""Trade journal — one row per CLOSED paper trade, kept forever (unlike the
ledger JSON, which only holds current state). This is the actual "learning
data": which pattern/confidence/trade-style combos won vs lost, over time.
"""

import csv
from pathlib import Path

from app.paper.models import Position

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PATH = ROOT / "data" / "trade_journal.csv"

FIELDNAMES = [
    "closed_at",
    "direction",
    "pattern",
    "confidence",
    "entry",
    "stop_loss",
    "take_profit",
    "outcome",
    "risk_percent",
    "reward_risk_ratio",
    "balance_before",
    "balance_after",
    "pnl",
]


def append_trade(closed_at: str, position: Position, outcome: str, balance_after: float, path: Path = DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()
    pnl = round(balance_after - position.balance_at_open, 2)

    row = {
        "closed_at": closed_at,
        "direction": position.direction,
        "pattern": position.pattern_name or "",
        "confidence": position.confidence,
        "entry": position.entry,
        "stop_loss": position.stop_loss,
        "take_profit": position.take_profit,
        "outcome": outcome,
        "risk_percent": position.risk_percent,
        "reward_risk_ratio": position.reward_risk_ratio,
        "balance_before": position.balance_at_open,
        "balance_after": balance_after,
        "pnl": pnl,
    }
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if is_new:
            writer.writeheader()
        writer.writerow(row)
