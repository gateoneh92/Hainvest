import streamlit as st
import requests
import pandas as pd

from data import (
    fetch_price_and_fundamentals,
    fetch_chart_history,
    fetch_news,
    get_quarterly_income,
)
from ai import run_ai_debate, run_portfolio_analysis
from ui import (
    resolve_single, resolve_multi,
    render_price_bar, render_fundamentals, render_candlestick_chart,
    render_consensus, render_agent_cards, render_verdict,
    render_share_button, render_backtest_chart,
    signal_badge,
)

# ── 1. Page config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="HaiInvestor", page_icon="👋", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }

    .app-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 16px; padding: 28px 36px; margin-bottom: 28px; text-align: center;
    }
    .app-header h1 { color: #fff; font-size: 2.2rem; margin: 0; letter-spacing: 2px; }
    .app-header p  { color: #aaa; margin: 8px 0 0; font-size: 0.95rem; }

    .price-bar {
        background: #1a1a2e; border-radius: 12px; padding: 18px 24px;
        margin-bottom: 16px; display: flex; gap: 32px; align-items: center; flex-wrap: wrap;
    }
    .price-ticker { color: #fff; font-size: 1.6rem; font-weight: 800; }
    .price-value  { color: #fff; font-size: 1.4rem; font-weight: 700; }
    .price-up     { color: #00e676; font-weight: 600; }
    .price-down   { color: #ff5252; font-weight: 600; }
    .price-meta   { color: #aaa; font-size: 0.8rem; }

    .consensus-box {
        background: #16213e; border-radius: 14px; padding: 20px 24px;
        margin-bottom: 28px; border: 1px solid #0f3460;
    }
    .consensus-title { color: #e0e0e0; font-size: 1rem; font-weight: 700; margin-bottom: 14px; letter-spacing: 1px; }

    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; letter-spacing: 1px; }
    .badge-bull { background: #00e67622; color: #00e676; border: 1px solid #00e676; }
    .badge-bear { background: #ff525222; color: #ff5252; border: 1px solid #ff5252; }
    .badge-neut { background: #ffd74022; color: #ffd740; border: 1px solid #ffd740; }

    .agent-card { background: #16213e; border-radius: 14px; padding: 20px 22px; margin-bottom: 16px; border-left: 4px solid #0f3460; border: 1px solid #1e2d50; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
    .agent-card-bull { border-left: 4px solid #00e676; border-color: #00e67633; }
    .agent-card-bear { border-left: 4px solid #ff5252; border-color: #ff525233; }
    .agent-card-neut { border-left: 4px solid #ffd740; border-color: #ffd74033; }
    .agent-name { color: #fff; font-size: 1rem; font-weight: 700; margin-bottom: 6px; }
    .agent-conf { color: #aaa; font-size: 0.8rem; margin-bottom: 10px; }
    .agent-text { color: #ccc; font-size: 0.88rem; line-height: 1.6; }

    .conf-bar-bg { background: #0a0a1a; border-radius: 4px; height: 6px; width: 100%; margin: 8px 0 12px; overflow: hidden; }
    .conf-bar-fill-bull { background: #00e676; height: 100%; border-radius: 4px; }
    .conf-bar-fill-bear { background: #ff5252; height: 100%; border-radius: 4px; }
    .conf-bar-fill-neut { background: #ffd740; height: 100%; border-radius: 4px; }

    .verdict-buy  { background: #00e67611; border: 2px solid #00e676; border-radius: 16px; padding: 24px; text-align: center; }
    .verdict-sell { background: #ff525211; border: 2px solid #ff5252; border-radius: 16px; padding: 24px; text-align: center; }
    .verdict-hold { background: #ffd74011; border: 2px solid #ffd740; border-radius: 16px; padding: 24px; text-align: center; }
    .verdict-label { font-size: 2.2rem; font-weight: 900; letter-spacing: 3px; }
    .verdict-label-buy  { color: #00e676; }
    .verdict-label-sell { color: #ff5252; }
    .verdict-label-hold { color: #ffd740; }
    .verdict-sub  { color: #ccc; font-size: 0.9rem; margin-top: 10px; line-height: 1.6; }
    .verdict-conf { color: #aaa; font-size: 0.8rem; margin-top: 8px; }

    .disclaimer { background: #1a1a2e; border-radius: 10px; padding: 14px 20px; color: #666; font-size: 0.78rem; margin-top: 32px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ── 2. API key ─────────────────────────────────────────────────────────────────
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("API Key is missing. Please check your .streamlit/secrets.toml file.")
    st.stop()

# ── 3. Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>👋 HaiInvestor</h1>
    <p>New to investing? Just pick a stock — 6 legendary AI investors will debate it for you.</p>
    <div style="margin-top:14px; display:flex; justify-content:center; gap:10px; flex-wrap:wrap;">
        <span style="background:#ffffff11; border:1px solid #ffffff22; border-radius:20px; padding:4px 12px; font-size:0.78rem; color:#ccc;">👴 Warren Buffett</span>
        <span style="background:#ffffff11; border:1px solid #ffffff22; border-radius:20px; padding:4px 12px; font-size:0.78rem; color:#ccc;">🧠 Charlie Munger</span>
        <span style="background:#ffffff11; border:1px solid #ffffff22; border-radius:20px; padding:4px 12px; font-size:0.78rem; color:#ccc;">🐻 Michael Burry</span>
        <span style="background:#ffffff11; border:1px solid #ffffff22; border-radius:20px; padding:4px 12px; font-size:0.78rem; color:#ccc;">🏃 Peter Lynch</span>
        <span style="background:#ffffff11; border:1px solid #ffffff22; border-radius:20px; padding:4px 12px; font-size:0.78rem; color:#ccc;">🚀 Cathie Wood</span>
        <span style="background:#ffffff11; border:1px solid #ffffff22; border-radius:20px; padding:4px 12px; font-size:0.78rem; color:#ccc;">⚔️ Bill Ackman</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 4. Language selector ───────────────────────────────────────────────────────
col_lang = st.columns([3, 1])[1]
with col_lang:
    lang = st.radio("🌐 Language", ["English", "한국어"], horizontal=True,
                    label_visibility="collapsed", key="lang_radio")
LANG = lang

# ── 5. Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Single Stock", "💼 Portfolio", "📈 Backtest"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SINGLE STOCK
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    with st.expander("❓ How does this work? (Click to read)"):
        st.markdown("""
**📊 Single Stock — Analyze one stock with 6 AI investors**

Pick any stock and let 6 legendary AI investors debate it using real news and financial data.

**How to use**
1. Click one of the quick buttons (AAPL, NVDA, etc.) or type any ticker in the search box.
2. The AI will analyze the latest news and real financial data, then each investor gives their opinion.

**How to read the results**
| Element | What it means |
|---------|---------------|
| Price bar | Current price, today's change, day high/low |
| Fundamentals cards | Key numbers: P/E ratio, market cap, revenue growth, etc. |
| Candlestick chart | 6-month price history |
| BULLISH 🟢 | This investor thinks the stock will go **up** |
| BEARISH 🔴 | This investor thinks the stock will go **down** |
| NEUTRAL 🟡 | This investor is **unsure** |
| Conviction % | How confident the AI is — higher means a stronger opinion |
| BUY / SELL / HOLD | Final verdict: buy it / sell it / wait |

> ⚠️ This is AI-generated analysis for educational purposes only. Always make your own investment decisions.
""")

    st.markdown("#### 🔥 Popular Stocks")
    c1, c2, c3, c4, c5 = st.columns(5)
    target_ticker = None
    if c1.button("🍎 AAPL", use_container_width=True): target_ticker = "AAPL"
    if c2.button("🟩 NVDA", use_container_width=True): target_ticker = "NVDA"
    if c3.button("🚗 TSLA", use_container_width=True): target_ticker = "TSLA"
    if c4.button("🪟 MSFT", use_container_width=True): target_ticker = "MSFT"
    if c5.button("📦 AMZN", use_container_width=True): target_ticker = "AMZN"

    st.markdown("<br>", unsafe_allow_html=True)
    custom = st.text_input("🔍 Search by ticker or company name",
                           placeholder="e.g., Apple, NVDA, Tesla, Bitcoin", key="single_input")
    if custom:
        target_ticker = resolve_single(custom, key_suffix="single")

    if target_ticker:
        st.markdown("---")
        with st.spinner(f"Fetching data for {target_ticker}..."):
            try:
                price, fund = fetch_price_and_fundamentals(target_ticker)
            except Exception as e:
                st.error(f"Could not fetch data: {e}")
                st.stop()

        render_price_bar(target_ticker, price)

        try:
            render_candlestick_chart(fetch_chart_history(target_ticker, "6mo"))
        except Exception:
            pass

        render_fundamentals(fund)

        with st.spinner("Convening the AI Hedge Fund Panel... ⏳"):
            try:
                news   = fetch_news(target_ticker)
                result = run_ai_debate(target_ticker, news, fund, OPENAI_API_KEY, LANG)
                render_consensus(target_ticker, result)
                render_agent_cards(result)
                render_verdict(result)

                mgr     = result.get("Manager", {})
                verdict = mgr.get("verdict", "HOLD")
                v_emoji = {"BUY": "📗", "SELL": "📕"}.get(verdict, "📒")
                tweet   = (
                    f"I just ran ${target_ticker} through 6 legendary AI investors on HaiInvestor.\n\n"
                    f"Verdict: {v_emoji} {verdict}\n\n"
                    f"Try it yourself 👇\nhttps://ainvest-jnpzmtom62rulztvu24d6c.streamlit.app"
                )
                render_share_button(tweet)
            except Exception as e:
                st.error(f"An error occurred: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PORTFOLIO
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 💼 Portfolio Analyzer")
    with st.expander("❓ How does this work? (Click to read)"):
        st.markdown("""
**💼 Portfolio — Compare and allocate across multiple stocks**

Enter several stocks at once and the AI will analyze each one, then suggest how to split your investment between them.

**How to use**
1. Type up to 6 ticker symbols separated by commas — e.g. `AAPL, NVDA, TSLA`
2. Click **Analyze Portfolio** and the AI will evaluate each stock.

**How to read the results**
| Element | What it means |
|---------|---------------|
| BUY / SELL / HOLD | AI's final opinion on each stock |
| Conviction % | How confident the AI is — higher = stronger opinion |
| Weight | Suggested allocation % among BULLISH stocks only |
| Pie chart | Visual breakdown of the suggested allocation |

**Example:** If AAPL gets 70% and NVDA gets 30%, a $1,000 portfolio would put $700 in AAPL and $300 in NVDA.

> ⚠️ Weights are calculated automatically from AI conviction scores. Use as a reference only, not as financial advice.
""")
    st.caption("Enter multiple tickers to get AI signals for each and suggested portfolio weights.")

    portfolio_input = st.text_input(
        "Enter tickers or company names, separated by commas",
        placeholder="e.g., Apple, NVDA, Tesla, Microsoft",
        key="portfolio_input",
    )

    if st.button("🚀 Analyze Portfolio", use_container_width=True, key="portfolio_btn"):
        tickers = resolve_multi(portfolio_input)
        if not tickers:
            st.warning("Enter at least one ticker.")
        elif len(tickers) > 6:
            st.warning("Maximum 6 tickers at once.")
        else:
            results_list = []
            progress = st.progress(0, text="Analyzing...")

            for i, ticker in enumerate(tickers):
                progress.progress(i / len(tickers), text=f"Analyzing {ticker}...")
                try:
                    price, fund = fetch_price_and_fundamentals(ticker)
                    news        = fetch_news(ticker)
                    ai          = run_portfolio_analysis(ticker, news, fund, OPENAI_API_KEY, LANG)
                    results_list.append({
                        "ticker":     ticker,
                        "price":      price["current"],
                        "change_pct": price["change_pct"],
                        "signal":     ai.get("signal", "NEUTRAL"),
                        "confidence": ai.get("confidence", 50),
                        "verdict":    ai.get("verdict", "HOLD"),
                        "summary":    ai.get("summary", ""),
                        "mktcap":     fund.get("Market Cap", "N/A"),
                        "pe":         fund.get("P/E (TTM)", "N/A"),
                    })
                except Exception as e:
                    results_list.append({
                        "ticker": ticker, "price": 0, "change_pct": 0,
                        "signal": "NEUTRAL", "confidence": 0, "verdict": "HOLD",
                        "summary": f"Error: {e}", "mktcap": "N/A", "pe": "N/A",
                    })
                progress.progress((i + 1) / len(tickers), text=f"Done: {ticker}")

            progress.empty()

            # Suggested weights (bullish conviction only)
            bull_stocks = [r for r in results_list if r["signal"] == "BULLISH"]
            total_conf  = sum(r["confidence"] for r in bull_stocks) or 1
            for r in results_list:
                r["weight"] = f"{int(r['confidence'] / total_conf * 100)}%" if r["signal"] == "BULLISH" else "—"

            # Results table
            st.markdown("#### 📋 Portfolio Summary")
            for r in results_list:
                sig     = r["signal"]
                chg     = r["change_pct"]
                chg_c   = "#00e676" if chg >= 0 else "#ff5252"
                chg_s   = f"▲ {abs(chg):.1f}%" if chg >= 0 else f"▼ {abs(chg):.1f}%"
                v_color = {"BUY": "#00e676", "SELL": "#ff5252"}.get(r["verdict"], "#ffd740")
                border  = "#00e676" if sig == "BULLISH" else "#ff5252" if sig == "BEARISH" else "#ffd740"
                st.markdown(f"""
<div style="background:#16213e; border-radius:12px; padding:16px 20px; margin-bottom:12px;
            border-left:4px solid {border};">
  <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
    <div>
      <span style="color:#fff; font-size:1.1rem; font-weight:800;">{r['ticker']}</span>
      <span style="color:#aaa; font-size:0.85rem; margin-left:10px;">${r['price']:,.2f}</span>
      <span style="color:{chg_c}; font-size:0.85rem; margin-left:8px;">{chg_s}</span>
    </div>
    <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
      {signal_badge(sig)}
      <span style="color:{v_color}; font-weight:700; font-size:0.9rem;">{r['verdict']}</span>
      <span style="color:#aaa; font-size:0.8rem;">Conviction: {r['confidence']}%</span>
      <span style="color:#0079C1; font-size:0.85rem; font-weight:700;">Weight: {r['weight']}</span>
    </div>
  </div>
  <div style="color:#aaa; font-size:0.82rem; margin-top:8px;">{r['summary']}</div>
  <div style="color:#666; font-size:0.75rem; margin-top:4px;">Market Cap: {r['mktcap']} &nbsp;|&nbsp; P/E: {r['pe']}</div>
</div>""", unsafe_allow_html=True)

            # Pie chart
            import plotly.graph_objects as go
            bull_for_pie = [r for r in results_list if r["signal"] == "BULLISH"]
            if bull_for_pie:
                st.markdown("#### 🥧 Suggested Allocation (Bullish Only)")
                fig_pie = go.Figure(go.Pie(
                    labels=[r["ticker"] for r in bull_for_pie],
                    values=[r["confidence"] for r in bull_for_pie],
                    hole=0.4,
                    marker_colors=["#00e676", "#0079C1", "#ffd740", "#9c27b0", "#ff9800", "#00bcd4"],
                ))
                fig_pie.update_layout(
                    paper_bgcolor="#16213e", font_color="#ccc",
                    height=300, margin=dict(l=10, r=10, t=10, b=10),
                    showlegend=True,
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No BULLISH signals — consider waiting for a better entry point.")

            ticker_list = ", ".join(f"${r['ticker']}" for r in results_list)
            buy_list    = ", ".join(f"${r['ticker']}" for r in results_list if r["verdict"] == "BUY") or "none"
            tweet = (
                f"I just analyzed a portfolio with HaiInvestor AI 📊\n\n"
                f"Tickers: {ticker_list}\n"
                f"AI says BUY: {buy_list}\n\n"
                f"Try it yourself 👇\nhttps://ainvest-jnpzmtom62rulztvu24d6c.streamlit.app"
            )
            render_share_button(tweet)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — BACKTEST
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📈 AI Signal Backtest")
    with st.expander("❓ How does this work? (Click to read)"):
        st.markdown("""
**📈 AI Signal Backtest — What if you followed the AI's logic historically?**

This simulates what would have happened if you invested based on the same fundamentals our AI panel looks at — every quarter, for the past 1–5 years.

**How to use**
1. Enter a ticker symbol (e.g. `NVDA`)
2. Select a time period (1 year / 2 years / 5 years)
3. Click **Run Backtest**

**How the signal is generated (same logic as our AI investors)**
Each quarter, we check two things Warren Buffett, Peter Lynch, and others actually care about:
- 📈 Is revenue **growing** compared to last quarter?
- 💰 Is the company **profitable** (positive profit margin)?

| Condition | Signal |
|-----------|--------|
| Revenue growing AND profitable | 🟢 BULLISH → Buy |
| Revenue shrinking OR losing money | 🔴 BEARISH → Sell |
| Mixed signals | 🟡 NEUTRAL → Hold cash |

**How to read the results**
| Metric | What it means |
|--------|---------------|
| AI Signal Return | Return if you followed the fundamental signals |
| Buy & Hold Return | Return if you just bought and never sold |
| Max Drawdown | Worst loss from peak — smaller is better |
| Quarters Invested | How many quarters the signal said "hold the stock" |

> ⚠️ Past performance does not guarantee future results. For educational purposes only.
""")
    st.caption("Simulates returns based on quarterly fundamental signals — the same logic our AI investors use.")

    bt_col1, bt_col2, bt_col3 = st.columns([2, 1, 1])
    with bt_col1:
        bt_input = st.text_input("Ticker or company name",
                                 placeholder="e.g., NVDA, Apple, Tesla", key="bt_input")
    with bt_col2:
        bt_period = st.selectbox("Period", ["1y", "2y", "5y"], index=1)
    with bt_col3:
        st.markdown("<br>", unsafe_allow_html=True)
        run_bt = st.button("▶ Run Backtest", use_container_width=True)

    bt_ticker = resolve_single(bt_input, key_suffix="bt") if bt_input else None

    if run_bt and bt_ticker:
        with st.spinner("Running backtest..."):
            try:
                income = get_quarterly_income(bt_ticker)
                if income is None or income.empty:
                    st.error("No quarterly financial data available for this ticker.")
                else:
                    rev_row = next((r for r in ["Total Revenue", "Revenue"] if r in income.index), None)
                    inc_row = next((r for r in ["Net Income", "Net Income Common Stockholders"] if r in income.index), None)

                    if not rev_row:
                        st.error("Revenue data not available for this ticker.")
                    else:
                        rev = income.loc[rev_row].sort_index()
                        net = income.loc[inc_row].sort_index() if inc_row else None

                        signals_df = pd.DataFrame({"revenue": rev})
                        signals_df["rev_growth"] = signals_df["revenue"].pct_change()
                        if net is not None:
                            signals_df["profitable"] = net.reindex(signals_df.index) > 0
                        else:
                            signals_df["profitable"] = True

                        def quarter_signal(row):
                            if pd.isna(row["rev_growth"]): return 0
                            growing    = row["rev_growth"] > 0
                            profitable = row.get("profitable", True)
                            if growing and profitable: return 1
                            if not growing:            return 0
                            return 0.5

                        signals_df["signal"] = signals_df.apply(quarter_signal, axis=1)
                        signals_df["signal"] = signals_df["signal"].shift(1).fillna(0)

                        hist_bt = fetch_chart_history(bt_ticker, bt_period)[["Close"]].copy()
                        if hist_bt.empty or len(hist_bt) < 20:
                            st.error("Not enough price history.")
                        else:
                            hist_bt.index = hist_bt.index.tz_localize(None)
                            signals_df.index = pd.to_datetime(signals_df.index).tz_localize(None)

                            hist_bt["signal"] = 0.0
                            for date, sig in signals_df["signal"].items():
                                hist_bt.loc[hist_bt.index >= date, "signal"] = sig

                            hist_bt["ret"]       = hist_bt["Close"].pct_change()
                            hist_bt["strat"]     = hist_bt["signal"] * hist_bt["ret"]
                            hist_bt["bah_cum"]   = (1 + hist_bt["ret"]).cumprod()
                            hist_bt["strat_cum"] = (1 + hist_bt["strat"]).cumprod()
                            hist_bt = hist_bt.dropna()

                            bah_ret   = (hist_bt["bah_cum"].iloc[-1] - 1) * 100
                            strat_ret = (hist_bt["strat_cum"].iloc[-1] - 1) * 100
                            rolling_max = hist_bt["strat_cum"].cummax()
                            max_dd      = ((hist_bt["strat_cum"] - rolling_max) / rolling_max).min() * 100
                            q_invested  = int((signals_df["signal"] > 0).sum())

                            m1, m2, m3, m4 = st.columns(4)
                            strat_delta = f"{'▲' if strat_ret >= bah_ret else '▼'} vs Buy & Hold"
                            m1.metric("AI Signal Return",  f"{strat_ret:+.1f}%", strat_delta)
                            m2.metric("Buy & Hold Return", f"{bah_ret:+.1f}%")
                            m3.metric("Max Drawdown",      f"{max_dd:.1f}%")
                            m4.metric("Quarters Invested", f"{q_invested}")

                            render_backtest_chart(hist_bt, bt_ticker)

                            with st.expander("📋 View quarterly signals"):
                                display_df = signals_df[["revenue", "rev_growth", "signal"]].copy()
                                display_df.index = (
                                    display_df.index.strftime("%Y-Q%q")
                                    if hasattr(display_df.index, "strftime") else display_df.index
                                )
                                display_df["revenue"]    = display_df["revenue"].apply(
                                    lambda x: f"${x/1e9:.2f}B" if pd.notna(x) else "N/A")
                                display_df["rev_growth"] = display_df["rev_growth"].apply(
                                    lambda x: f"{x*100:+.1f}%" if pd.notna(x) else "N/A")
                                display_df["signal"]     = display_df["signal"].map(
                                    {1: "🟢 BULLISH", 0.5: "🟡 NEUTRAL", 0: "🔴 BEARISH"})
                                display_df.columns = ["Revenue", "QoQ Growth", "Signal"]
                                st.dataframe(display_df.tail(12), use_container_width=True)

            except Exception as e:
                st.error(f"Backtest error: {e}")


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
    ⚠️ <b>Disclaimer:</b> This AI analysis is a simulation based on public news and financial data.
    Not financial advice. Always do your own research before making investment decisions.
</div>
""", unsafe_allow_html=True)

try:
    r     = requests.get("https://api.counterapi.dev/v1/hainvestor/visits/up", timeout=3)
    count = r.json().get("count", "—")
except Exception:
    count = "—"

st.markdown(f"""
<div style='text-align:center; margin:16px 0 4px; color:#555; font-size:0.78rem;'>
    🧪 Beta Users: <b style='color:#666;'>{count}</b>
</div>
""", unsafe_allow_html=True)

with st.expander("😤 Hate this app?", expanded=False):
    st.markdown(
        "Think our AI panel is full of garbage? **Pay $1 and leave your best insult in the PayPal note.** I'll read every single one.",
        unsafe_allow_html=False
    )
    st.link_button("💸 Pay $1 to Insult Me", "https://www.paypal.com/ncp/payment/A3Q3JEV6WRXSG",
                   use_container_width=False)
