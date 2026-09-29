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
    return cfg
