"""Shared data shape for Phase 7."""

from dataclasses import dataclass


@dataclass
class PatternStats:
    name: str
    count: int
    hits: int
    hit_rate: float  # percent

    def to_dict(self) -> dict:
        return {"name": self.name, "count": self.count, "hits": self.hits, "hit_rate": self.hit_rate}
