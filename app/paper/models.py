"""Shared data shape for the paper-trading ledger — simulated P&L only, no real orders."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Position:
    direction: str  # "BUY" | "SELL"
    entry: float
    stop_loss: float
    take_profit: float
    balance_at_open: float
    risk_percent: float
    reward_risk_ratio: float
    opened_at: str


@dataclass
class LedgerState:
    balance: float
    position: Optional[Position] = None
    trade_count: int = 0
    win_count: int = 0
