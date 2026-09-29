# Gold (XAU/USD) Trading Signal System — Full Flow

Ek hi file me pura flow, phases, aur konse API key kahan se milenge — taaki baad me idhar-udhar dhoondhna na pade.

## Kaise kaam karta hai (Architecture)

```
[Twelve Data: Price+Volume] --\
[Pattern/Volume Engine (local)] ---> compact JSON summary --> [Claude API] --> {signal, confidence, reason}
[Finnhub: News headlines] ----/
```

Claude sirf final decision layer hai. Pattern detection, volume analysis, aur historical matching sab local code (free, fast) karta hai — Claude ko sirf ek chhota structured summary bhejte hain, taaki token cost minimum rahe.

Har phase ek fixed JSON schema output karta hai, agla phase sirf usko consume karta hai. Isliye naya phase (backtesting, risk management, broker execution) baad me add karne se purane phases todhne/rewrite karne ki zaroorat nahi padegi.

## Phases

| # | Phase | Kaam | Aapko kya dena hoga |
|---|---|---|---|
| 0 | Setup | `.env` files, project structure, logging | kuch nahi (is step me ho gaya) |
| 1 | Data Ingestion | XAU/USD OHLC (price) fetch — historical + live | `TWELVE_DATA_API_KEY` |
| 2 | Pattern & Volume Engine | Candlestick pattern + support/resistance + volume-spike ratio (local logic, no API) | kuch nahi |
| 3 | News Ingestion | Gold/USD/Fed related latest headlines | `FINNHUB_API_KEY` |
| 4 | Claude Decision Layer | Phase 2+3 ka summary Claude ko bhej ke BUY/SELL/HOLD signal lena | `ANTHROPIC_API_KEY` |
| 5 | Scheduler | Phase 1→4 ko cron/loop se automatic chalana | decide: local machine ya server/VPS pe chalega |
| 6 | Output & Logging | Signal store (CSV) + notify (Telegram/console) | (optional) `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| 7 (future) | Backtesting | Pattern/volume thresholds ko historical data pe tune karna | zyada historical data range (same Phase 1 provider) |
| 8 (future) | Risk Management | Stop-loss/take-profit, position sizing | aapka risk tolerance / account size |
| 9 (future) | Broker Execution | Signal ko real order me convert (sirf agar chaho) | broker API keys + har trade ki manual confirmation |

## Free API Keys — kahan se milenge

### 1. Price data → Twelve Data
- URL: https://twelvedata.com
- Free tier: ~800 requests/day, XAU/USD (gold) forex pair supported, intraday candles milte hain
- No credit card required signup ke liye
- Signup karke "API Key" dashboard se copy karo → `.env.development` me `TWELVE_DATA_API_KEY=` ke aage paste karo
- **Volume note:** gold/forex OTC market hai — Twelve Data isme `volume: 0` deta hai (OANDA jaisa broker real tick-volume deta, lekin OANDA India me register nahi hota — RBI/FEMA restriction). Isliye Phase 2 me real volume ki jagah **volatility-based proxy** (candle range / ATR — jitna bada price move utna zyada "activity") use karenge. Koi naya signup nahi chahiye iske liye.

### 2. News headlines → Finnhub
- URL: https://finnhub.io
- Free tier: ~60 calls/min, general market news endpoint (forex/gold relevant filter kar sakte hain)
- No credit card required
- Signup → dashboard se API key copy → `.env.development` me `FINNHUB_API_KEY=`

### 3. Claude API → Anthropic Console
- URL: https://console.anthropic.com
- Ye key main nahi la sakta — account aapka hona chahiye (billing bhi aapke account se judi hai)
- Key generate karke `.env.development` me `ANTHROPIC_API_KEY=`

### 4. (Optional, Phase 6) Telegram notifications
- @BotFather (Telegram app me) se free bot bana ke token milega
- `TELEGRAM_BOT_TOKEN` aur apna `TELEGRAM_CHAT_ID`

## Env files

- `.env.example` — template, git me committed rehta hai (koi real key nahi)
- `.env.development` / `.env.stage` / `.env.prod` — inme real keys dalo, ye gitignored hain (kabhi commit nahi honge)
- Local run ke liye `.env.development` use hoga; jab live/paisa-wala mode chalega tab `.env.prod`

## Code Standards (Phase 0 se follow karna hai, har phase me)

- **Max ~500-600 lines per file.** Isse zyada ho raha ho toh file split karo.
- **Common/reusable logic ek jagah:** `app/helpers.py` (reusable functions jaise masking, formatting) aur `app/constants.py` (shared data jaise key lists, phase list) — 2+ jagah use hone wala code yahi jaayega, koi bhi file me duplicate nahi hoga.
- **Ek file = ek responsibility:** `config.py` sirf env loading karta hai, `main.py` sirf CLI entrypoint hai, `ui/dashboard.py` sirf UI render karta hai. Business logic (Phase 1 onwards: data fetch, pattern detection, Claude call) apni alag file/module me jayega, UI/CLI files me nahi.
- Naya phase start hote hi uska code apne alag file/folder me jayega (e.g. `app/data/`, `app/patterns/`, `app/news/`, `app/decision/`), purani files ko touch kiye bina.

## Ab kya karna hai

Batao Phase 1 se kitne tak abhi build karna hai (suggestion: Phase 1-6 = ek working MVP), aur upar wali table me jo keys chahiye woh `.env.development` me daal do — code likhna shuru karte hain.
