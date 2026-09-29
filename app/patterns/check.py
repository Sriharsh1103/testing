"""Manual verification for Phase 2: python -m app.patterns.check [env_name]"""

import sys

from app.data.service import get_candles
from app.patterns.engine import analyze


def main() -> None:
    env_name = sys.argv[1] if len(sys.argv) > 1 else None
    candles = get_candles(env_name, output_size=50)
    snapshot = analyze(candles)

    print(f"[Phase 2] Analyzed {len(candles)} candles")
    for key, value in snapshot.to_dict().items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
