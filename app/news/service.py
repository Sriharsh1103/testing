"""Public entry point for Phase 3 — config-aware, this is what Phase 4 imports."""

from typing import List, Optional

from app.config import load_config
from app.news.filters import filter_relevant
from app.news.finnhub_client import fetch_news
from app.news.models import NewsItem

MIN_RELEVANT_ITEMS = 3
DEFAULT_LIMIT = 5


def get_headlines(env_name: Optional[str] = None, limit: int = DEFAULT_LIMIT) -> List[NewsItem]:
    cfg = load_config(env_name)
    api_key = cfg["FINNHUB_API_KEY"]
    if not api_key:
        raise RuntimeError("FINNHUB_API_KEY is not set — add it to your .env file.")

    # "forex" category is throttled to ~1 item on Finnhub's free tier; "general"
    # gets the full feed, and we keyword-filter it down to gold-relevant headlines.
    items = fetch_news(category="general", api_key=api_key)
    relevant = filter_relevant(items)

    # Fall back to the unfiltered feed if keyword filtering leaves too little to work with
    selected = relevant if len(relevant) >= MIN_RELEVANT_ITEMS else items
    return selected[:limit]
