"""Shared data shape for Phase 3 — Phase 4 (Claude layer) consumes NewsItem.to_dict()."""

from dataclasses import dataclass


@dataclass
class NewsItem:
    headline: str
    source: str
    datetime: str  # ISO 8601, UTC
    url: str

    def to_dict(self) -> dict:
        return {
            "headline": self.headline,
            "source": self.source,
            "datetime": self.datetime,
            "url": self.url,
        }
