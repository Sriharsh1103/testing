"""Manual run for Phase 7: python -m app.backtest.check [env_name] [candle_count] [horizon]"""

import sys

from app.backtest.engine import DEFAULT_HORIZON, run_backtest
from app.data.service import get_candles


def main() -> None:
    args = sys.argv[1:]
    env_name = args[0] if len(args) > 0 else None
    count = int(args[1]) if len(args) > 1 else 500
    horizon = int(args[2]) if len(args) > 2 else DEFAULT_HORIZON

    candles = get_candles(env_name, output_size=count)
    results = run_backtest(candles, horizon=horizon)

    print(f"[Phase 7] Backtested {len(candles)} candles, horizon={horizon} candles ahead")
    if not results:
        print("  No patterns detected in this window.")
        return

    for r in results:
        print(f"  {r.name}: {r.count} occurrences, {r.hits} hits, {r.hit_rate}% hit-rate")


if __name__ == "__main__":
    main()
