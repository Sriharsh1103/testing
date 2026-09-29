#!/usr/bin/env bash
# Usage: ./run.sh [development|stage|prod]
set -e

ENV_NAME="${1:-development}"
export APP_ENV="$ENV_NAME"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f ".venv/bin/activate" ]; then
    echo "Creating virtualenv (.venv) ..."
    python3 -m venv .venv
fi
source .venv/bin/activate

pip install -q -r requirements.txt

echo "Starting Phase 0 dashboard in '$ENV_NAME' mode..."
streamlit run app/ui/dashboard.py
