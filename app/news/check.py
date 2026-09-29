"""Manual verification for Phase 3: python -m app.news.check [env_name]"""

import sys

from app.news.service import get_headlines


def main() -> None:
    env_name = sys.argv[1] if len(sys.argv) > 1 else None
    headlines = get_headlines(env_name)

    print(f"[Phase 3] Fetched {len(headlines)} relevant headlines")
    for h in headlines:
        print(f"  [{h.datetime}] {h.headline} ({h.source})")


if __name__ == "__main__":
    main()
