"""Keyword-based relevance filtering — pure functions over NewsItem data, no I/O."""

from typing import List, Optional

from app.news.models import NewsItem

GOLD_RELEVANT_KEYWORDS = [
    "gold", "fed", "fomc", "inflation", "rate", "dollar", "usd",
    "treasury", "yield", "cpi", "jobs", "nonfarm", "powell",
    "safe haven", "geopolitical", "war", "recession",
]


def filter_relevant(items: List[NewsItem], keywords: Optional[List[str]] = None) -> List[NewsItem]:
    keywords = keywords or GOLD_RELEVANT_KEYWORDS
    return [item for item in items if any(k in item.headline.lower() for k in keywords)]
