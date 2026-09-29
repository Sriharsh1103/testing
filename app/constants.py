"""Shared constants used across config, CLI, and UI — single source of truth."""

REQUIRED_KEYS = [
    "TWELVE_DATA_API_KEY",
    "FINNHUB_API_KEY",
    "ANTHROPIC_API_KEY",
]

OPTIONAL_KEYS = [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
]

ENVS = ["development", "stage", "prod"]

# (phase_label, description, status) — status: "done" | "pending"
PHASES = [
    ("Phase 0", "Setup (.env files, project skeleton, dashboard)", "done"),
    ("Phase 1", "Data Ingestion — price (Twelve Data)", "done"),
    ("Phase 2", "Pattern & Volume Engine (local)", "done"),
    ("Phase 3", "News Ingestion (Finnhub)", "done"),
    ("Phase 4", "Claude Decision Layer", "pending"),
    ("Phase 5", "Scheduler", "pending"),
    ("Phase 6", "Output & Logging (Telegram/console)", "done"),
    ("Phase 7", "Pattern Backtest (historical hit-rate)", "done"),
    ("Phase 8", "Risk Management (stop-loss / take-profit)", "done"),
]
