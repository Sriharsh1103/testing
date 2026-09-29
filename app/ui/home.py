"""Home — the live trading dashboard. Everything loads automatically, no manual
fetch buttons. Real API/Claude calls are cache-throttled (see cache.py), so
"Auto-refresh" just re-renders from cache most of the time — cheap and safe.

The paper-trading ledger and Telegram signal/close messages are only ever
written by the standalone scheduler (app/scheduler/runner.py) — this page only
*reads* the ledger, so an auto-refreshing browser tab can never double-fire a
trade or a duplicate message. See README.
"""

import csv
import time

import streamlit as st
from dotenv import set_key

from app.backtest.engine import DEFAULT_HORIZON, run_backtest
from app.config import env_file_for, load_config
from app.constants import HOLD_DURATION_HINT, TRADE_STYLES
from app.decision.models import TradeSignal
from app.risk.models import RiskPlan
from app.output.csv_store import DEFAULT_PATH as SIGNALS_CSV_PATH
from app.output.formatting import format_message
from app.output.telegram_notifier import send_message
from app.paper import journal, storage as paper_storage
from app.patterns.engine import analyze
from app.risk.service import get_risk_plan
from app.scheduler.session import is_active_session
from app.ui.cache import CANDLES_TTL, get_candles, get_headlines, get_trade_signal_with_snapshot

AUTO_REFRESH_SECONDS = 30


def _render_trading_settings(active_env: str, cfg: dict) -> None:
    with st.expander("Trading settings", expanded=False):
        env_path = env_file_for(active_env)

        style_names = list(TRADE_STYLES.keys())
        current_style = cfg["TRADE_STYLE"] if cfg["TRADE_STYLE"] in style_names else "Intraday"
        style = st.selectbox("Trade style", style_names, index=style_names.index(current_style))
        if style != current_style:
            set_key(str(env_path), "TRADE_STYLE", style)
            set_key(str(env_path), "TIMEFRAME", TRADE_STYLES[style])
            st.cache_data.clear()
            st.success(f"Switched to {style} ({TRADE_STYLES[style]} chart). Reloading...")
            st.rerun()

        new_balance = st.number_input(
            "Paper trading — initial balance (₹ INR)",
            min_value=1.0,
            value=cfg["PAPER_INITIAL_BALANCE"],
            step=1000.0,
        )
        col1, col2 = st.columns(2)
        if col1.button("Save initial balance"):
            set_key(str(env_path), "PAPER_INITIAL_BALANCE", str(new_balance))
            st.success("Saved — applies next time the ledger is reset.")
        if col2.button("Reset paper account now"):
            paper_storage.reset(active_env, new_balance)
            st.success(f"Paper ledger reset to {new_balance}.")


def _render_price_and_pattern(active_env: str):
    st.markdown("### Price & pattern")
    try:
        candles = get_candles(active_env, 50)
        rows = [c.to_dict() for c in candles]
        st.line_chart({"close": [r["close"] for r in rows]})

        snapshot = analyze(candles)
        col1, col2, col3 = st.columns(3)
        col1.metric("Last close", snapshot.last_close)
        col2.metric("Support", snapshot.support)
        col3.metric("Resistance", snapshot.resistance)

        if snapshot.pattern:
            st.success(f"Pattern: **{snapshot.pattern.name}** ({snapshot.pattern.bias})")
        else:
            st.caption("No pattern on the latest candle")
        st.caption(
            f"Volatility (volume proxy): {snapshot.volatility.label} "
            f"— ratio {snapshot.volatility.ratio} · data cached {CANDLES_TTL}s"
        )
        return snapshot
    except Exception as exc:  # noqa: BLE001
        st.error(f"Price/pattern unavailable: {exc}")
        return None


def _render_news(active_env: str):
    st.markdown("### News")
    try:
        headlines = get_headlines(active_env)
        for h in headlines[:5]:
            st.write(f"- {h.headline}")
    except Exception as exc:  # noqa: BLE001
        st.error(f"News unavailable: {exc}")


def _render_signal_and_risk(active_env: str, cfg: dict):
    st.markdown("### Claude trade signal")
    st.caption(
        "Preview only — the scheduler process is what actually logs/notifies/trades on this "
        "(Telegram fires only for an actual BUY/SELL call, not HOLD)."
    )
    try:
        signal, snapshot, _last_candle = get_trade_signal_with_snapshot(active_env)
        color = {"BUY": "success", "SELL": "error", "HOLD": "warning"}.get(signal.signal, "info")
        getattr(st, color)(f"**{signal.signal}** — confidence {signal.confidence}%")
        st.write(signal.reason)

        plan = get_risk_plan(active_env, signal, snapshot)
        if plan:
            c1, c2, c3 = st.columns(3)
            c1.metric("Entry (USD)", plan.entry)
            c2.metric("Stop-loss (USD)", plan.stop_loss)
            c3.metric("Take-profit (USD)", plan.take_profit)

            balance = paper_storage.load(active_env, cfg["PAPER_INITIAL_BALANCE"]).balance
            risk_amount = round(balance * plan.risk_percent / 100, 2)
            reward_amount = round(risk_amount * plan.reward_risk_ratio, 2)
            st.caption(
                f"Risk: ₹{risk_amount} of ₹{round(balance, 2)} ({plan.risk_percent}%) "
                f"| Potential: ₹{reward_amount} | Suggested hold: {HOLD_DURATION_HINT.get(cfg['TRADE_STYLE'], '—')}"
            )
    except Exception as exc:  # noqa: BLE001
        st.error(f"Trade signal unavailable: {exc}")


def _render_paper_ledger(active_env: str, cfg: dict):
    st.markdown("### Paper trading account")
    st.caption("Simulated only — updated automatically by the scheduler, every tick.")
    state = paper_storage.load(active_env, cfg["PAPER_INITIAL_BALANCE"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Balance (₹)", round(state.balance, 2))
    c2.metric("Trades closed", state.trade_count)
    win_rate = round(state.win_count / state.trade_count * 100, 1) if state.trade_count else 0.0
    c3.metric("Win rate", f"{win_rate}%")

    if state.position:
        p = state.position
        st.info(
            f"Open: **{p.direction}** @ {p.entry} | SL {p.stop_loss} | TP {p.take_profit} "
            f"(opened {p.opened_at})"
        )
    else:
        st.caption("No open position.")


def _render_trade_journal():
    st.markdown("### Trade journal (learning data)")
    st.caption("One row per closed trade — pattern, confidence, and outcome, for future analysis.")
    if not journal.DEFAULT_PATH.exists():
        st.caption("No trades closed yet — nothing to learn from until the scheduler closes its first one.")
        return

    with journal.DEFAULT_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    st.dataframe(rows[-20:], use_container_width=True, hide_index=True)

    by_pattern: dict = {}
    for r in rows:
        p = r["pattern"] or "(none)"
        by_pattern.setdefault(p, {"count": 0, "wins": 0})
        by_pattern[p]["count"] += 1
        if r["outcome"] == "TP":
            by_pattern[p]["wins"] += 1
    if by_pattern:
        summary = [
            {"Pattern": p, "Trades": v["count"], "Win rate": f"{round(v['wins'] / v['count'] * 100, 1)}%"}
            for p, v in by_pattern.items()
        ]
        st.dataframe(summary, use_container_width=True, hide_index=True)


def _render_backtest(active_env: str):
    st.markdown("### Pattern backtest (historical hit-rate)")
    try:
        big_candles = get_candles(active_env, 500)
        results = run_backtest(big_candles, horizon=DEFAULT_HORIZON)
        if results:
            st.dataframe([r.to_dict() for r in results], use_container_width=True, hide_index=True)
        else:
            st.caption("No patterns detected in this window.")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Backtest unavailable: {exc}")


def _render_output_log(active_env: str, cfg: dict):
    with st.expander("Output log & test notification (manual — not part of auto-refresh)"):
        if SIGNALS_CSV_PATH.exists():
            with SIGNALS_CSV_PATH.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            st.caption(f"Signal log: `{SIGNALS_CSV_PATH}` ({len(rows)} rows)")
            st.dataframe(rows[-10:], use_container_width=True, hide_index=True)
        else:
            st.caption("No signals logged yet — the scheduler (Phase 5) appends here.")

        if st.button("Send test Telegram message"):
            try:
                bot_token, chat_id = cfg["TELEGRAM_BOT_TOKEN"], cfg["TELEGRAM_CHAT_ID"]
                if not bot_token or not chat_id:
                    st.warning("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set.")
                else:
                    balance = paper_storage.load(active_env, cfg["PAPER_INITIAL_BALANCE"]).balance
                    test_signal = TradeSignal(signal="BUY", confidence=70, reason="Dashboard test message.")
                    test_plan = RiskPlan(
                        entry=0.0, stop_loss=0.0, take_profit=0.0,
                        risk_percent=cfg["RISK_PER_TRADE_PCT"], reward_risk_ratio=cfg["REWARD_RISK_RATIO"],
                    )
                    text = format_message(
                        test_signal, cfg["SYMBOL"], risk_plan=test_plan,
                        hold_duration=HOLD_DURATION_HINT.get(cfg["TRADE_STYLE"]), balance_inr=balance,
                    )
                    send_message(bot_token, chat_id, text)
                    st.success("Sent — check your Telegram chat.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not send Telegram message: {exc}")


def render(active_env: str) -> None:
    st.subheader("Live trading dashboard")
    cfg = load_config(active_env)

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        auto_refresh = st.checkbox("Auto-refresh (every 30s)", value=False)
    with col_b:
        active = is_active_session()
        st.caption(f"Session: **{'active' if active else 'idle'}**")
    with col_c:
        st.caption(f"Style: **{cfg['TRADE_STYLE']}** ({cfg['TIMEFRAME']})")

    _render_trading_settings(active_env, cfg)
    _render_price_and_pattern(active_env)
    _render_news(active_env)
    _render_signal_and_risk(active_env, cfg)
    _render_paper_ledger(active_env, cfg)
    _render_trade_journal()
    _render_backtest(active_env)
    _render_output_log(active_env, cfg)

    if auto_refresh:
        time.sleep(AUTO_REFRESH_SECONDS)
        st.rerun()
