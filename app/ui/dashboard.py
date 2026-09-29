import csv
import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.config import env_file_for, load_config  # noqa: E402
from app.constants import ENVS, PHASES, REQUIRED_KEYS, OPTIONAL_KEYS  # noqa: E402
from app.data.service import get_candles  # noqa: E402
from app.backtest.engine import DEFAULT_HORIZON, run_backtest  # noqa: E402
from app.decision.models import TradeSignal  # noqa: E402
from app.decision.service import get_trade_signal  # noqa: E402
from app.helpers import mask_secret  # noqa: E402
from app.news.service import get_headlines  # noqa: E402
from app.patterns.engine import analyze  # noqa: E402
from app.output.csv_store import DEFAULT_PATH as SIGNALS_CSV_PATH  # noqa: E402
from app.output.formatting import format_message  # noqa: E402
from app.output.telegram_notifier import send_message  # noqa: E402
from app.risk.service import get_risk_plan  # noqa: E402
from app.scheduler.session import is_active_session  # noqa: E402

st.set_page_config(page_title="Gold Signal System — Setup", layout="centered")

st.title("Gold (XAU/USD) Signal System")
st.caption("Phase 0 — setup & environment check")

active_env = os.getenv("APP_ENV", "development")
st.info(f"Active environment (APP_ENV): **{active_env}**")

st.subheader("Environment key status")


def render_key_group(label: str, keys: list[str], values: dict, required: bool) -> None:
    st.markdown(f"**{label}**")
    for key in keys:
        val = values.get(key, "")
        if val:
            st.success(f"{key}: set ({mask_secret(val)})")
        elif required:
            st.warning(f"{key}: missing")
        else:
            st.caption(f"{key}: not set")


for env_name in ENVS:
    env_path = env_file_for(env_name)
    marker = " (active)" if env_name == active_env else ""
    with st.expander(f"{env_name}{marker} — {env_path.name}", expanded=(env_name == active_env)):
        if not env_path.exists():
            st.error(f"File not found: {env_path}")
            continue
        values = dotenv_values(env_path)
        render_key_group("Required", REQUIRED_KEYS, values, required=True)
        render_key_group("Optional", OPTIONAL_KEYS, values, required=False)

st.subheader("Phase 1 — Live price data")
st.caption("Manual fetch (won't auto-run on every page load, to save API quota)")

if st.button("Fetch latest candles"):
    try:
        candles = get_candles(active_env, output_size=20)
        rows = [c.to_dict() for c in candles]
        st.success(f"Fetched {len(rows)} candles for {active_env}")
        st.dataframe(rows, use_container_width=True)
        st.line_chart({"close": [r["close"] for r in rows]})
        if all(r["volume"] == 0 for r in rows):
            st.caption("Volume is 0 for all candles — expected for XAU/USD (OTC market), Phase 2 uses a volatility proxy instead.")
    except Exception as exc:  # noqa: BLE001 — surface any fetch/config error to the UI
        st.error(f"Could not fetch candles: {exc}")

st.subheader("Phase 2 — Pattern & volatility analysis")
st.caption("Local computation only, no API call — runs on the last 50 candles")

if st.button("Analyze latest data"):
    try:
        candles = get_candles(active_env, output_size=50)
        snapshot = analyze(candles).to_dict()

        col1, col2, col3 = st.columns(3)
        col1.metric("Last close", snapshot["last_close"])
        col2.metric("Support", snapshot["support"])
        col3.metric("Resistance", snapshot["resistance"])

        pattern = snapshot["pattern"]
        if pattern:
            st.success(f"Pattern: **{pattern['name']}** ({pattern['bias']})")
        else:
            st.caption("Pattern: none detected on the latest candle")

        vol = snapshot["volatility"]
        st.write(f"Volatility (volume proxy): **{vol['label']}** — ratio {vol['ratio']} (ATR {vol['atr']})")
    except Exception as exc:  # noqa: BLE001 — surface any fetch/config error to the UI
        st.error(f"Could not analyze: {exc}")

st.subheader("Phase 3 — News headlines")
st.caption("Manual fetch (won't auto-run on every page load, to save API quota)")

if st.button("Fetch latest news"):
    try:
        headlines = get_headlines(active_env)
        st.success(f"Fetched {len(headlines)} relevant headlines")
        for h in headlines:
            st.write(f"- **{h.headline}** — {h.source} ({h.datetime})")
    except Exception as exc:  # noqa: BLE001 — surface any fetch/config error to the UI
        st.error(f"Could not fetch news: {exc}")

st.subheader("Phase 4 — Claude trade signal")
st.caption("Combines Phase 2 + Phase 3 output, calls Claude (claude-haiku-4-5) once")

if st.button("Get trade signal"):
    try:
        signal = get_trade_signal(active_env)
        color = {"BUY": "success", "SELL": "error", "HOLD": "warning"}.get(signal.signal, "info")
        getattr(st, color)(f"**{signal.signal}** — confidence {signal.confidence}%")
        st.write(signal.reason)
    except Exception as exc:  # noqa: BLE001 — surface any fetch/config/API error to the UI
        st.error(f"Could not get signal: {exc}")

st.subheader("Phase 5 — Scheduler status")
try:
    _cfg = load_config(active_env)
    _active = is_active_session()
    _interval = _cfg["POLL_INTERVAL_ACTIVE_MIN"] if _active else _cfg["POLL_INTERVAL_IDLE_MIN"]
    st.write(
        f"Session: **{'active (London-NY overlap)' if _active else 'idle'}** — "
        f"polling every **{_interval} min**"
    )
    st.caption("Run the actual loop separately: `python -m app.scheduler.runner " + active_env + "`")
except Exception as exc:  # noqa: BLE001
    st.error(f"Could not read scheduler config: {exc}")

st.subheader("Phase 6 — Output & logging")

if SIGNALS_CSV_PATH.exists():
    with SIGNALS_CSV_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    st.caption(f"Signal log: `{SIGNALS_CSV_PATH}` ({len(rows)} rows)")
    st.dataframe(rows[-10:], use_container_width=True)
else:
    st.caption("No signals logged yet — signals are appended here once Phase 4/5 run.")

if st.button("Send test Telegram message"):
    try:
        _cfg = load_config(active_env)
        bot_token = _cfg["TELEGRAM_BOT_TOKEN"]
        chat_id = _cfg["TELEGRAM_CHAT_ID"]
        if not bot_token or not chat_id:
            st.warning("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set — nothing to test.")
        else:
            test_signal = TradeSignal(signal="HOLD", confidence=50, reason="Dashboard test message.")
            send_message(bot_token, chat_id, format_message(test_signal, _cfg["SYMBOL"]))
            st.success("Sent — check your Telegram chat.")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not send Telegram message: {exc}")

st.subheader("Phase 7 — Pattern backtest")
st.caption("No Claude call — checks historical hit-rate of each pattern before it feeds Phase 4")

if st.button("Run backtest (last 500 candles)"):
    try:
        candles = get_candles(active_env, output_size=500)
        results = run_backtest(candles, horizon=DEFAULT_HORIZON)
        if not results:
            st.caption("No patterns detected in this window.")
        else:
            st.dataframe([r.to_dict() for r in results], use_container_width=True)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not run backtest: {exc}")

st.subheader("Phase 8 — Risk management (stop-loss / take-profit)")
st.caption(
    "No account size used — shows %-risk only (see README). "
    "Direction is picked manually here since Phase 4 is credit-blocked; "
    "the scheduler (Phase 5) wires this to the real Claude signal automatically."
)

_direction = st.selectbox("Signal direction (example)", ["BUY", "SELL"])
if st.button("Compute risk plan"):
    try:
        candles = get_candles(active_env, output_size=50)
        snapshot = analyze(candles)
        example_signal = TradeSignal(signal=_direction, confidence=70, reason="Dashboard example")
        plan = get_risk_plan(active_env, example_signal, snapshot)
        col1, col2, col3 = st.columns(3)
        col1.metric("Entry", plan.entry)
        col2.metric("Stop-loss", plan.stop_loss)
        col3.metric("Take-profit", plan.take_profit)
        st.caption(f"Risk: {plan.risk_percent}% of capital — risk:reward 1:{plan.reward_risk_ratio}")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not compute risk plan: {exc}")

st.subheader("Roadmap")
for phase, desc, status in PHASES:
    icon = "✅" if status == "done" else "⬜"
    st.write(f"{icon} **{phase}** — {desc}")

st.divider()
st.caption("Fill missing keys in the matching .env.<environment> file, then rerun this dashboard.")
