import sys

from app.config import load_config
from app.constants import REQUIRED_KEYS, OPTIONAL_KEYS
from app.helpers import key_status


def main() -> None:
    env_name = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = load_config(env_name)

    print(f"[Phase 0] Environment: {cfg['ENV']}")
    print(f"[Phase 0] Symbol: {cfg['SYMBOL']}  Timeframe: {cfg['TIMEFRAME']}")
    print()
    print("Required keys:")
    for key in REQUIRED_KEYS:
        print(f"  {key}: {key_status(cfg[key])}")

    print("Optional keys:")
    for key in OPTIONAL_KEYS:
        print(f"  {key}: {key_status(cfg[key])}")

    print()
    print("Phase 0 setup check complete. Run the dashboard with: ./run.sh")


if __name__ == "__main__":
    main()
