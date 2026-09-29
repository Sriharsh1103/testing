"""Raw Finnhub API access — fetch + parse only, no config/env knowledge here."""

from datetime import datetime, timezone
from typing import List

import requests

from app.news.models import NewsItem

BASE_URL = "https://finnhub.io/api/v1/news"


class FinnhubError(Exception):
    pass


def fetch_news(category: str, api_key: str) -> List[NewsItem]:
    """Fetch latest news for `category` (general | forex | crypto | merger), newest-first."""
    params = {"category": category, "token": api_key}
    response = requests.get(BASE_URL, params=params, timeout=15)

    if response.status_code != 200:
        raise FinnhubError(f"Finnhub error ({response.status_code}): {response.text}")

    items = [
        NewsItem(
            headline=item["headline"],
            source=item.get("source", ""),
            datetime=datetime.fromtimestamp(item["datetime"], tz=timezone.utc).isoformat(),
            url=item.get("url", ""),
        )
        for item in response.json()
        if item.get("headline")
    ]
    items.sort(key=lambda n: n.datetime, reverse=True)
    return items
