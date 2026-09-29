"""Persists the paper-trading ledger to a local JSON file, one per environment."""

import json
from dataclasses import asdict
from pathlib import Path

from app.paper.models import LedgerState, Position

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"


def path_for(env_name: str) -> Path:
    return DATA_DIR / f"paper_ledger_{env_name}.json"


def load(env_name: str, initial_balance: float) -> LedgerState:
    path = path_for(env_name)
    if not path.exists():
        return LedgerState(balance=initial_balance)

    data = json.loads(path.read_text())
    position = Position(**data["position"]) if data.get("position") else None
    return LedgerState(
        balance=data["balance"],
        position=position,
        trade_count=data.get("trade_count", 0),
        win_count=data.get("win_count", 0),
    )


def save(env_name: str, state: LedgerState) -> None:
    path = path_for(env_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "balance": state.balance,
        "position": asdict(state.position) if state.position else None,
        "trade_count": state.trade_count,
        "win_count": state.win_count,
    }
    path.write_text(json.dumps(data, indent=2))


def reset(env_name: str, initial_balance: float) -> LedgerState:
    state = LedgerState(balance=initial_balance)
    save(env_name, state)
    return state
