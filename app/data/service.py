"""Public entry point for Phase 1 — config-aware, this is what Phase 2/5 import."""

from typing import List, Optional

from app.config import load_config
from app.data.models import Candle
from app.data.twelve_data_client import fetch_time_series


def get_candles(env_name: Optional[str] = None, output_size: int = 100) -> List[Candle]:
    cfg = load_config(env_name)
    api_key = cfg["TWELVE_DATA_API_KEY"]
    if not api_key:
        raise RuntimeError("TWELVE_DATA_API_KEY is not set — add it to your .env file.")

    return fetch_time_series(
        symbol=cfg["SYMBOL"],
        interval=cfg["TIMEFRAME"],
        api_key=api_key,
        output_size=output_size,
    )
