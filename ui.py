import streamlit as st
import plotly.graph_objects as go
import requests

from data import search_ticker


AGENTS_ORDER = [
    ("Warren",  "👴", "Warren Buffett",  "Value Investor"),
    ("Charlie", "🧠", "Charlie Munger",  "Mental Models"),
    ("Michael", "🐻", "Michael Burry",   "Contrarian Bear"),
    ("Peter",   "🏃", "Peter Lynch",     "GARP Investor"),
    ("Cathie",  "🚀", "Cathie Wood",     "Innovation Bull"),
    ("Bill",    "⚔️", "Bill Ackman",     "Activist Investor"),
]


# ── Signal helpers ─────────────────────────────────────────────────────────────

def signal_badge(sig):
    if sig == "BULLISH": return '<span class="badge badge-bull">▲ BULLISH</span>'
    if sig == "BEARISH": return '<span class="badge badge-bear">▼ BEARISH</span>'
    return '<span class="badge badge-neut">◆ NEUTRAL</span>'

def signal_card_class(sig):
    return {"BULLISH": "agent-card-bull", "BEARISH": "agent-card-bear"}.get(sig, "agent-card-neut")

def signal_bar_class(sig):
    return {"BULLISH": "conf-bar-fill-bull", "BEARISH": "conf-bar-fill-bear"}.get(sig, "conf-bar-fill-neut")


# ── Ticker resolution (interactive UI helpers) ─────────────────────────────────

def resolve_single(query, key_suffix=""):
    """Resolve a company name or ticker to a ticker symbol.
    If all-uppercase (≤8 chars, no spaces), treated as a direct ticker.
    Otherwise searches Yahoo Finance and shows a selectbox."""
    q = query.strip()
    if not q:
        return None
    if q == q.upper() and len(q) <= 8 and " " not in q:
        return q.upper()
    with st.spinner("Searching..."):
        results = search_ticker(q)
    if not results:
        st.warning(f"No results found for '{q}'. Try a ticker symbol instead.")
        return None
    options = {f"{name} ({symbol})": symbol for symbol, name in results}
    chosen  = st.selectbox("Select the stock you meant:", list(options.keys()), key=f"search_{key_suffix}")
    if chosen:
        ticker = options[chosen]
        st.caption(f"✅ Resolved: **{ticker}**")
        return ticker
    return None


def resolve_multi(raw_input):
    """Resolve comma-separated company names/tickers to a list of ticker symbols.
    All-uppercase tokens (≤8 chars) are used directly; others are searched."""
    tokens  = [t.strip() for t in raw_input.split(",") if t.strip()]
    tickers = []
    for t in tokens:
        if t == t.upper() and len(t) <= 8 and " " not in t:
            tickers.append(t.upper())
        else:
            results = search_ticker(t)
            if results:
                tickers.append(results[0][0])
                st.caption(f"'{t}' → **{results[0][0]}** ({results[0][1]})")
            else:
                st.warning(f"Could not find ticker for '{t}', skipping.")
    return tickers


# ── Render: price bar ──────────────────────────────────────────────────────────

def render_price_bar(ticker, price):
    d_class = "price-up" if price["change"] >= 0 else "price-down"
    d_sign  = "▲" if price["change"] >= 0 else "▼"
    st.markdown(f"""
<div class="price-bar">
    <span class="price-ticker">{ticker}</span>
    <span class="price-value">${price['current']:,.2f}</span>
    <span class="{d_class}">{d_sign} {abs(price['change']):.2f} ({abs(price['change_pct']):.2f}%)</span>
    <span class="price-meta">Day: ${price['low']:,.2f} – ${price['high']:,.2f}</span>
</div>""", unsafe_allow_html=True)


# ── Render: fundamentals cards ─────────────────────────────────────────────────

def render_fundamentals(fund):
    html = "<div style='display:flex; flex-wrap:wrap; gap:10px; margin-bottom:20px;'>"
    for label, value in fund.items():
        if value == "N/A":
            continue
        html += f"""<div style='background:#1a1a2e; border-radius:10px; padding:12px 18px; min-width:110px;'>
            <div style='color:#aaa; font-size:0.72rem; margin-bottom:4px;'>{label}</div>
            <div style='color:#fff; font-size:1rem; font-weight:700;'>{value}</div></div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ── Render: 6-month candlestick chart ─────────────────────────────────────────

def render_candlestick_chart(hist):
    if hist.empty:
        return
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist["Open"], high=hist["High"],
        low=hist["Low"],   close=hist["Close"],
        increasing_line_color="#00e676", decreasing_line_color="#ff5252",
        name="Price",
    ))
    fig.update_layout(
        paper_bgcolor="#16213e", plot_bgcolor="#16213e",
        font_color="#ccc", height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(gridcolor="#0f3460", showgrid=True, rangeslider_visible=False),
        yaxis=dict(gridcolor="#0f3460", showgrid=True),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Render: panel consensus bar ────────────────────────────────────────────────

def render_consensus(ticker, result):
    signals  = [result[k]["signal"] for k, *_ in AGENTS_ORDER if k in result]
    bull_n   = signals.count("BULLISH")
    bear_n   = signals.count("BEARISH")
    neut_n   = signals.count("NEUTRAL")
    total    = len(signals) or 1
    bull_pct = int(bull_n / total * 100)
    bear_pct = int(bear_n / total * 100)
    neut_pct = int(neut_n / total * 100)
    st.markdown(f"""
<div class="consensus-box">
    <div class="consensus-title">⚖️ PANEL CONSENSUS — {ticker}</div>
    <div style="display:flex; gap:24px; margin-bottom:12px;">
        <span>{signal_badge('BULLISH')} &nbsp;<b style="color:#fff">{bull_n}</b><span style="color:#aaa"> / {total}</span></span>
        <span>{signal_badge('BEARISH')} &nbsp;<b style="color:#fff">{bear_n}</b><span style="color:#aaa"> / {total}</span></span>
        <span>{signal_badge('NEUTRAL')} &nbsp;<b style="color:#fff">{neut_n}</b><span style="color:#aaa"> / {total}</span></span>
    </div>
    <div style="display:flex; height:10px; border-radius:6px; overflow:hidden; background:#0a0a1a;">
        <div style="width:{bull_pct}%; background:#00e676;"></div>
        <div style="width:{neut_pct}%; background:#ffd740;"></div>
        <div style="width:{bear_pct}%; background:#ff5252;"></div>
    </div>
    <div style="display:flex; justify-content:space-between; margin-top:4px;">
        <span style="color:#00e676; font-size:0.75rem;">{bull_pct}% Bullish</span>
        <span style="color:#ffd740; font-size:0.75rem;">{neut_pct}% Neutral</span>
        <span style="color:#ff5252; font-size:0.75rem;">{bear_pct}% Bearish</span>
    </div>
</div>""", unsafe_allow_html=True)


# ── Render: individual investor cards ─────────────────────────────────────────

def render_agent_cards(result):
    st.markdown("### 🗣️ Investor Perspectives")
    col_l, col_r = st.columns(2)
    for i, (key, icon, name, role) in enumerate(AGENTS_ORDER):
        data = result.get(key, {})
        sig  = data.get("signal", "NEUTRAL")
        conf = data.get("confidence", 50)
        text = data.get("reasoning", "")
        html = f"""<div class="agent-card {signal_card_class(sig)}">
    <div class="agent-name">{icon} {name} <span style="color:#aaa; font-weight:400; font-size:0.8rem;">· {role}</span></div>
    {signal_badge(sig)}
    <div class="conf-bar-bg"><div class="{signal_bar_class(sig)}" style="width:{conf}%;"></div></div>
    <div class="agent-conf">Conviction: {conf}%</div>
    <div class="agent-text">{text}</div>
</div>"""
        (col_l if i % 2 == 0 else col_r).markdown(html, unsafe_allow_html=True)


# ── Render: portfolio manager verdict ─────────────────────────────────────────

def render_verdict(result):
    st.markdown("### 🏦 Portfolio Manager's Final Verdict")
    mgr       = result.get("Manager", {})
    verdict   = mgr.get("verdict", "HOLD")
    m_conf    = mgr.get("confidence", 50)
    action    = mgr.get("action", "")
    rationale = mgr.get("rationale", "")
    v_class   = {"BUY": "verdict-buy",       "SELL": "verdict-sell"      }.get(verdict, "verdict-hold")
    l_class   = {"BUY": "verdict-label-buy", "SELL": "verdict-label-sell"}.get(verdict, "verdict-label-hold")
    v_icon    = {"BUY": "📗", "SELL": "📕"}.get(verdict, "📒")
    st.markdown(f"""<div class="{v_class}">
    <div class="verdict-label {l_class}">{v_icon} {verdict}</div>
    <div class="verdict-sub"><b>{action}</b><br><br>{rationale}</div>
    <div class="verdict-conf">Portfolio Manager Conviction: {m_conf}%</div>
</div>""", unsafe_allow_html=True)


# ── Render: share on X button ─────────────────────────────────────────────────

def render_share_button(tweet_text):
    tweet_url = f"https://twitter.com/intent/tweet?text={requests.utils.quote(tweet_text)}"
    st.markdown(f"""
<div style="text-align:center; margin-top:24px;">
    <a href="{tweet_url}" target="_blank"
       style="background:#1DA1F2; color:white; padding:10px 24px; border-radius:20px;
              text-decoration:none; font-weight:700; font-size:0.9rem;">
        🐦 Share on X (Twitter)
    </a>
</div>
""", unsafe_allow_html=True)


# ── Render: backtest chart ────────────────────────────────────────────────────

def render_backtest_chart(hist_bt, bt_ticker):
    fig = go.Figure()
    # Shade bullish periods
    in_bull = False
    bull_start = None
    for idx, row in hist_bt.iterrows():
        if row["signal"] > 0 and not in_bull:
            bull_start = idx
            in_bull = True
        elif row["signal"] == 0 and in_bull:
            fig.add_vrect(x0=bull_start, x1=idx,
                fillcolor="rgba(0,230,118,0.07)", line_width=0)
            in_bull = False
    if in_bull:
        fig.add_vrect(x0=bull_start, x1=hist_bt.index[-1],
            fillcolor="rgba(0,230,118,0.07)", line_width=0)

    fig.add_trace(go.Scatter(
        x=hist_bt.index, y=hist_bt["bah_cum"],
        name="Buy & Hold", line=dict(color="#aaa", width=1.5, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=hist_bt.index, y=hist_bt["strat_cum"],
        name="AI Signal Strategy", line=dict(color="#00e676", width=2),
    ))
    fig.update_layout(
        paper_bgcolor="#16213e", plot_bgcolor="#16213e",
        font_color="#ccc", height=380,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor="#0f3460"),
        yaxis=dict(gridcolor="#0f3460", tickformat=".0%"),
        legend=dict(bgcolor="#0f0c29", bordercolor="#0f3460", borderwidth=1),
        title=dict(text=f"{bt_ticker} — AI Signal vs Buy & Hold (🟢 = Bullish periods)", font_color="#ccc"),
    )
    st.plotly_chart(fig, use_container_width=True)
