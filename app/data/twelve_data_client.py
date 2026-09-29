"""Raw Twelve Data API access — fetch + parse only, no config/env knowledge here.

Note: for XAU/USD (OTC gold/forex), Twelve Data's "volume" field is always 0 —
there is no single centralized exchange for spot gold/forex. Phase 2 computes
a volatility-based proxy (ATR/range) instead of relying on this field.
"""

import time
from typing import List, Optional

import requests

from app.data.models import Candle

BASE_URL = "https://api.twelvedata.com/time_series"
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 8  # free tier is rate-limited per minute, not per day


class TwelveDataError(Exception):
    pass


def fetch_time_series(
    symbol: str,
    interval: str,
    api_key: str,
    output_size: int = 100,
) -> List[Candle]:
    """Fetch OHLCV candles for `symbol`, oldest-first."""
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": output_size,
        "apikey": api_key,
        "format": "JSON",
    }

    last_error: Optional[Exception] = None
    for _ in range(MAX_RETRIES):
        response = requests.get(BASE_URL, params=params, timeout=15)
        data = response.json()

        if data.get("status") == "error":
            code = data.get("code")
            message = data.get("message", "unknown error")
            if code == 429:
                last_error = TwelveDataError(f"Rate limited: {message}")
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise TwelveDataError(f"Twelve Data error ({code}): {message}")

        values = data.get("values", [])
        candles = [
            Candle(
                datetime=v["datetime"],
                open=float(v["open"]),
                high=float(v["high"]),
                low=float(v["low"]),
                close=float(v["close"]),
                volume=float(v.get("volume") or 0),
            )
            for v in values
        ]
        candles.reverse()  # API returns newest-first; normalize to oldest-first
        return candles

    raise last_error or TwelveDataError("Failed to fetch data after retries")
