"""Phase 7 — backtests Phase 2's pattern detection against historical outcomes.

Deliberately no Claude calls: this checks whether pattern detection has any
predictive edge on real historical data *before* spending API tokens on
Phase 4. Support/resistance and volatility aren't scored here since they
aren't directional signals by themselves — only candlestick patterns are.
"""

from collections import defaultdict
from typing import List

from app.backtest.models import PatternStats
from app.data.models import Candle
from app.patterns.candlestick import detect_pattern

DEFAULT_HORIZON = 4  # candles ahead to check the outcome (4 x 15min = 1 hour)


def run_backtest(candles: List[Candle], horizon: int = DEFAULT_HORIZON) -> List[PatternStats]:
    counts = defaultdict(int)
    hits = defaultdict(int)

    for i in range(1, len(candles) - horizon):
        pattern = detect_pattern(candles[i - 1 : i + 1])
        if not pattern or pattern.bias == "neutral":
            continue

        entry_close = candles[i].close
        future_close = candles[i + horizon].close
        moved_up = future_close > entry_close
        hit = (pattern.bias == "bullish" and moved_up) or (pattern.bias == "bearish" and not moved_up)

        counts[pattern.name] += 1
        if hit:
            hits[pattern.name] += 1

    results = [
        PatternStats(
            name=name,
            count=count,
            hits=hits.get(name, 0),
            hit_rate=round(hits.get(name, 0) / count * 100, 1) if count else 0.0,
        )
        for name, count in counts.items()
    ]
    results.sort(key=lambda r: r.count, reverse=True)
    return results
