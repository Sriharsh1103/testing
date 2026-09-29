import os
from pathlib import Path

from dotenv import load_dotenv

from app.constants import REQUIRED_KEYS, OPTIONAL_KEYS

ROOT = Path(__file__).resolve().parent.parent


def env_file_for(env_name: str) -> Path:
    return ROOT / f".env.{env_name}"


def load_config(env_name: str | None = None) -> dict:
    env_name = env_name or os.getenv("APP_ENV", "development")
    env_file = env_file_for(env_name)
    if not env_file.exists():
        raise FileNotFoundError(f"Env file not found: {env_file}")

    load_dotenv(env_file, override=True)

    cfg = {"ENV": env_name}
    for key in REQUIRED_KEYS + OPTIONAL_KEYS:
        cfg[key] = os.getenv(key, "")
    cfg["SYMBOL"] = os.getenv("SYMBOL", "XAU/USD")
    cfg["TIMEFRAME"] = os.getenv("TIMEFRAME", "15min")
    cfg["TRADE_STYLE"] = os.getenv("TRADE_STYLE", "Intraday")
    cfg["POLL_INTERVAL_ACTIVE_MIN"] = int(os.getenv("POLL_INTERVAL_ACTIVE_MIN", "5"))
    cfg["POLL_INTERVAL_IDLE_MIN"] = int(os.getenv("POLL_INTERVAL_IDLE_MIN", "5"))
    # Phase 8 — risk management defaults (no account size, %-risk only; see README)
    cfg["RISK_PER_TRADE_PCT"] = float(os.getenv("RISK_PER_TRADE_PCT", "1.0"))
    cfg["ATR_STOP_MULTIPLIER"] = float(os.getenv("ATR_STOP_MULTIPLIER", "2.0"))
    cfg["REWARD_RISK_RATIO"] = float(os.getenv("REWARD_RISK_RATIO", "1.5"))
    # Paper-trading ledger (simulated, no real money/orders)
    cfg["PAPER_INITIAL_BALANCE"] = float(os.getenv("PAPER_INITIAL_BALANCE", "1000.0"))
    return cfg
