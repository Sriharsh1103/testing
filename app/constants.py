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

# Trade style -> chart timeframe (Twelve Data granularity) it analyzes
TRADE_STYLES = {
    "Scalping": "5min",
    "Intraday": "15min",
    "Swing": "4h",
}

# Trade style -> suggested hold duration, shown in the Telegram message
HOLD_DURATION_HINT = {
    "Scalping": "15-30 minutes",
    "Intraday": "2-6 hours (close same day)",
    "Swing": "1-3 days",
}

# (phase_label, description, status, pending_note) — status: "done" | "pending" | "on hold"
# pending_note explains what's blocking it, empty string when done.
PHASES = [
    ("Phase 0", "Setup (.env files, project skeleton, dashboard)", "done", ""),
    ("Phase 1", "Data Ingestion — price (Twelve Data)", "done", ""),
    ("Phase 2", "Pattern & Volume Engine (local)", "done", ""),
    ("Phase 3", "News Ingestion (Finnhub)", "done", ""),
    ("Phase 4", "Claude Decision Layer", "pending", "Blocked: Anthropic API credit balance too low"),
    ("Phase 5", "Scheduler", "pending", "Running in background every 5 min — waiting on Phase 4 credits to actually fire"),
    ("Phase 6", "Output & Logging (Telegram/console)", "done", ""),
    ("Phase 7", "Pattern Backtest (historical hit-rate)", "done", ""),
    ("Phase 8", "Risk Management (stop-loss / take-profit)", "done", ""),
    ("Phase 9", "Broker Execution", "on hold", "Held by user request — not started"),
]
