# HaiInvestor — Project Guide for Claude

## Project Overview
Streamlit-based AI stock analysis app. 6 legendary investor personas (Warren Buffett, Charlie Munger, etc.) debate a stock using real-time price data, fundamentals, and news headlines, then output a BUY/SELL/HOLD verdict.

**Live app:** https://ainvest-jnpzmtom62rulztvu24d6c.streamlit.app
**GitHub:** https://github.com/gateoneh92/Hainvest

---

## Module Structure

### `app.py` — Entrypoint & Orchestration
- Page config, CSS styles, header, language selector
- Tab layout: Single Stock / Portfolio / Backtest
- Calls functions from `data.py`, `ai.py`, `ui.py`
- **Do not put fetch logic, AI prompts, or render functions here**

### `data.py` — Data Fetching
- `fetch_price_and_fundamentals(ticker)` — price via `fast_info`, fundamentals via `tkr.info` (optional/graceful)
- `fetch_chart_history(ticker, period)` — OHLCV history for candlestick chart
- `fetch_news(ticker)` — Google News RSS headlines
- `search_ticker(query)` — Yahoo Finance company name → ticker search
- `get_quarterly_income(ticker)` — quarterly financials for backtest
- `fmt_val(val, ...)` — number formatting helper
- All fetch functions use `@st.cache_data` with appropriate TTLs
- **Do not put UI (st.*) calls or AI prompts here**

### `ai.py` — AI / OpenAI
- `run_ai_debate(ticker, news, fund, api_key, language)` — full 6-investor debate + portfolio manager verdict
- `run_portfolio_analysis(ticker, news, fund, api_key, language)` — lightweight single-signal analysis for portfolio tab
- Takes `api_key` as a parameter (do not access `st.secrets` here)
- **Do not put data fetching or UI calls here**

### `ui.py` — UI Components & Rendering
- `resolve_single(query, key_suffix)` — interactive ticker resolver (shows selectbox for company names)
- `resolve_multi(raw_input)` — resolves comma-separated list of names/tickers
- `render_price_bar(ticker, price)` — price + daily change display
- `render_fundamentals(fund)` — fundamentals cards grid
- `render_candlestick_chart(hist)` — 6-month candlestick chart
- `render_consensus(ticker, result)` — panel vote bar
- `render_agent_cards(result)` — 6 investor opinion cards (2-column layout)
- `render_verdict(result)` — final BUY/SELL/HOLD verdict box
- `render_share_button(tweet_text)` — X (Twitter) share link
- `render_backtest_chart(hist_bt, bt_ticker)` — strategy vs buy & hold chart
- `AGENTS_ORDER` — canonical order and metadata for the 6 investors
- **Do not put data fetching or AI prompt logic here**

---

## Key Rules

### File Hygiene
- Backup files are named `app_v*.py` (e.g. `app_v5.py`) — **always gitignored, never pushed**
- Create a backup before significant changes: `cp app.py app_vN.py`
- The `.gitignore` already covers `app_v*.py`

### When Adding Features
- New data source or yfinance call → add to `data.py`
- New AI prompt or OpenAI call → add to `ai.py`
- New UI component or render function → add to `ui.py`
- Tab logic and wiring → `app.py`

### Rate Limiting (Yahoo Finance)
- `fetch_price_and_fundamentals` uses `fast_info` first (lightweight), falls back to `history(5d)`
- `tkr.info` (fundamentals) is **always optional** — wrapped in try/except, returns N/A on failure
- Functions must always return a value (never raise for rate limits) so `@st.cache_data` caches the result

### Language Support
- Language toggle: `LANG` variable in `app.py` (`"English"` or `"한국어"`)
- Pass `language=LANG` to `run_ai_debate` and `run_portfolio_analysis`
- All 3 tabs must respect the language setting

### Tech Stack
| Layer | Library |
|-------|---------|
| Frontend | Streamlit |
| AI | OpenAI GPT-4o-mini |
| Market Data | yfinance 1.2.x |
| News | Google News RSS + BeautifulSoup |
| Charts | Plotly |
| Ticker Search | Yahoo Finance `/v1/finance/search` API |
