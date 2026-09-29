"""Manual verification for Phase 1: python -m app.data.check [env_name]"""

import sys

from app.data.service import get_candles


def main() -> None:
    env_name = sys.argv[1] if len(sys.argv) > 1 else None
    candles = get_candles(env_name, output_size=10)

    print(f"[Phase 1] Fetched {len(candles)} candles")
    for c in candles[-5:]:
        print(f"  {c.datetime}  O:{c.open} H:{c.high} L:{c.low} C:{c.close} V:{c.volume}")


if __name__ == "__main__":
    main()
