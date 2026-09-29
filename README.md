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
| 7 | Backtesting | Pattern detection ko historical data pe test karke hit-rate nikalna (no Claude call) | kuch nahi |
| 8 | Risk Management | Stop-loss/take-profit (ATR-based) + %-risk per trade | kuch nahi (defaults hain, `.env` me override kar sakte ho) |
| 9 (on hold) | Broker Execution | Signal ko real order me convert (sirf agar chaho) | broker API keys + har trade ki manual confirmation |

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

## Phase 8 — risk management defaults

Koi account size nahi use hoti (privacy/simplicity ke liye) — sirf %-risk aur price levels dikhte hain:
- `RISK_PER_TRADE_PCT=1.0` — har trade pe capital ka kitna % risk karna hai
- `ATR_STOP_MULTIPLIER=2.0` — stop-loss = entry se 2x ATR door
- `REWARD_RISK_RATIO=1.5` — take-profit = stop-distance ka 1.5x (risk:reward 1:1.5)

Teeno `.env.<environment>` me override ho sakte hain, code me defaults hain isliye set karna zaroori nahi.

## Fully automatic mode (scheduler + Telegram + paper trading)

Sirf dashboard khol ke rakhne se signals automatic nahi generate hote — dashboard sirf **preview** hai. Asli automatic pipeline ye standalone process hai:

```bash
python -m app.scheduler.runner development
```

Isko background me chalne do (nohup/screen/tmux/systemd — jo bhi aapke server pe standard ho). Har 5 min (`POLL_INTERVAL_ACTIVE_MIN`/`POLL_INTERVAL_IDLE_MIN`, dono default 5) pe:
1. Price + pattern + news + Claude signal generate hota hai
2. CSV log + Telegram message (entry/SL/TP ke saath) automatic jata hai
3. Paper-trading ledger update hota hai (naya trade khulta hai agar position khali hai, ya SL/TP hit check hota hai agar khula hua hai)

**Sirf yahi process** CSV/Telegram/paper-ledger ko likhta hai — dashboard ka "Home" page sirf **read-only preview** dikhata hai (apna khud ka cached Claude call, jo kabhi log/notify nahi karta), taaki dashboard khula rakhne se duplicate trades/messages na ho.

**Trade style** (Scalping/Intraday/Swing) Home page se select karo — turant `.env` me save hota hai, scheduler agli tick pe automatically naya timeframe use karega (restart ki zaroorat nahi, har tick pe config fresh read hota hai).

**Paper trading balance** — "Trading settings" me initial amount daalo, "Reset paper account" se kabhi bhi restart kar sakte ho. Real paisa/order kahi involve nahi hai, sirf simulated tracking hai.

**Abhi ka status:** Claude credits na hone ki wajah se scheduler har tick pe error print karta hai (crash nahi hota, Telegram bhi nahi jata jab tak error hai) — credits add hote hi automatically kaam karna shuru kar dega, kuch restart nahi karna padega.

## Trade journal — "learning data"

Paper-ledger sirf current state rakhta hai (balance, open position) — **har closed trade ka poora record** alag se `data/trade_journal.csv` me save hota hai: kaunsa pattern tha, kitna confidence tha, entry/SL/TP, outcome (TP/SL), aur P&L. Ye future me analyze karne ke liye hai — kaunsa pattern/confidence combo actually kaam kar raha hai, taaki thresholds (Phase 2) ya risk settings (Phase 8) ko tune kiya ja sake. Home page pe "Trade journal" section me recent trades + per-pattern win-rate dikhta hai.

Abhi tak koi trade close nahi hua (Claude credits pending hone ki wajah se koi signal hi nahi bana) — jaise hi real trades close honge, ye data apne aap accumulate hoga.

## Dashboard layout

`./run.sh` khol ke sidebar me 3 sections milenge:
- **Home** — live trading view (price chart, pattern, news, Claude signal, risk plan, backtest) — sab automatic load hota hai, koi manual "fetch" button nahi. "Auto-refresh" checkbox se har 30s page refresh hoga.
- **Environment** — `View` tab (masked key status) + `Secrets (edit)` tab (values edit karke seedha `.env.<environment>` file me save kar sakte ho)
- **Phases** — sabhi phases ka status table (kya karta hai, done/pending/on-hold, kya pending hai)

**Auto-refresh safe kyun hai:** UI har 30s refresh hoti hai lekin asli API/Claude calls `app/ui/cache.py` me cache hote hain (candles 5min, news 10min, Claude signal 15min) — isliye baar-baar refresh karne se paisa/quota nahi udhta, sirf cache se dikhta rehta hai.

## Code Standards (Phase 0 se follow karna hai, har phase me)

- **Max ~500-600 lines per file.** Isse zyada ho raha ho toh file split karo.
- **Common/reusable logic ek jagah:** `app/helpers.py` (reusable functions jaise masking, formatting) aur `app/constants.py` (shared data jaise key lists, phase list) — 2+ jagah use hone wala code yahi jaayega, koi bhi file me duplicate nahi hoga.
- **Ek file = ek responsibility:** `config.py` sirf env loading karta hai, `main.py` sirf CLI entrypoint hai, `ui/dashboard.py` sirf sidebar navigation hai (`ui/home.py`, `ui/environment.py`, `ui/phases.py` — har page apni file me). Business logic (Phase 1 onwards: data fetch, pattern detection, Claude call) apni alag file/module me jayega, UI/CLI files me nahi.
- Naya phase start hote hi uska code apne alag file/folder me jayega (e.g. `app/data/`, `app/patterns/`, `app/news/`, `app/decision/`), purani files ko touch kiye bina.

## Ab kya karna hai

Sab phases (0-8) ban chuke hain, Phase 9 hold pe hai. Sirf **Anthropic API credits** add karne baaki hain (console.anthropic.com → Plans & Billing) — uske baad scheduler automatically real signals generate karna, Telegram bhejna, aur paper-trading track karna shuru kar dega, kuch aur karna nahi padega.
