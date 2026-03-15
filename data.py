import streamlit as st
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import numpy as np
import time


def fmt_val(val, suffix="", multiplier=1, decimals=2):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    v = val * multiplier
    if suffix == "" and abs(v) >= 1e12: return f"${v/1e12:.1f}T"
    if suffix == "" and abs(v) >= 1e9:  return f"${v/1e9:.1f}B"
    if suffix == "" and abs(v) >= 1e6:  return f"${v/1e6:.1f}M"
    return f"{v:.{decimals}f}{suffix}"


@st.cache_data(ttl=600)
def fetch_price_and_fundamentals(ticker):
    """Returns (price_dict, fundamentals_dict). Cached 10 min.
    Price via fast_info (light). Fundamentals via tkr.info (optional — N/A on failure)."""
    from yfinance.exceptions import YFRateLimitError
    tkr = yf.Ticker(ticker)

    # ── Price via fast_info (single lightweight API call) ────────────────
    price = None
    try:
        fi  = tkr.fast_info
        cur = fi.last_price
        if cur:
            price = {
                "current": float(cur),
                "prev":    float(fi.regular_market_previous_close or cur),
                "high":    float(fi.day_high or cur),
                "low":     float(fi.day_low or cur),
            }
            price["change"]     = price["current"] - price["prev"]
            price["change_pct"] = price["change"] / price["prev"] * 100
    except (YFRateLimitError, Exception):
        pass  # fall through to history fallback

    # ── Fallback: history() if fast_info gave nothing ────────────────────
    if price is None:
        for attempt in range(3):
            try:
                hist = tkr.history(period="5d")
                if hist.empty:
                    raise ValueError(f"No price data found for '{ticker}'")
                price = {
                    "current": float(hist["Close"].iloc[-1]),
                    "prev":    float(hist["Close"].iloc[-2]) if len(hist) >= 2 else float(hist["Close"].iloc[-1]),
                    "high":    float(hist["High"].iloc[-1]),
                    "low":     float(hist["Low"].iloc[-1]),
                }
                price["change"]     = price["current"] - price["prev"]
                price["change_pct"] = price["change"] / price["prev"] * 100
                break
            except YFRateLimitError:
                if attempt < 2:
                    time.sleep(3 ** attempt)
                    continue
                raise
            except Exception:
                raise

    # ── Fundamentals via tkr.info (completely optional) ──────────────────
    fund_keys = ["Market Cap", "P/E (TTM)", "Forward P/E", "P/B Ratio",
                 "Revenue Growth", "Profit Margin", "ROE", "Debt/Equity"]
    try:
        info = tkr.info
        fund = {
            "Market Cap":     fmt_val(info.get("marketCap")),
            "P/E (TTM)":      fmt_val(info.get("trailingPE"),     decimals=1),
            "Forward P/E":    fmt_val(info.get("forwardPE"),      decimals=1),
            "P/B Ratio":      fmt_val(info.get("priceToBook"),    decimals=2),
            "Revenue Growth": fmt_val(info.get("revenueGrowth"),  suffix="%", multiplier=100, decimals=1),
            "Profit Margin":  fmt_val(info.get("profitMargins"),  suffix="%", multiplier=100, decimals=1),
            "ROE":            fmt_val(info.get("returnOnEquity"), suffix="%", multiplier=100, decimals=1),
            "Debt/Equity":    fmt_val(info.get("debtToEquity"),   decimals=2),
        }
    except Exception:
        fund = {k: "N/A" for k in fund_keys}

    return price, fund


@st.cache_data(ttl=3600)
def search_ticker(query):
    """Search Yahoo Finance by company name or ticker. Returns list of (symbol, name)."""
    try:
        url  = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}&newsCount=0&listsCount=0"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        data = resp.json()
        results = []
        for q in data.get("quotes", [])[:6]:
            if q.get("quoteType") in ["EQUITY", "ETF", "CRYPTOCURRENCY"]:
                symbol = q.get("symbol", "")
                name   = q.get("shortname") or q.get("longname") or symbol
                results.append((symbol, name))
        return results
    except Exception:
        return []


@st.cache_data(ttl=600)
def fetch_chart_history(ticker, period="6mo"):
    for attempt in range(3):
        try:
            return yf.Ticker(ticker).history(period=period)
        except Exception as e:
            if "429" in str(e) or "Too Many" in str(e) or "Rate" in str(e):
                time.sleep(2 ** attempt)
                continue
            raise
    return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_news(ticker):
    url  = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.content, "html.parser")
    items = soup.find_all("item")
    return "\n".join(f"- {it.title.text}" for it in items[:10])


@st.cache_data(ttl=3600)
def get_quarterly_income(ticker):
    return yf.Ticker(ticker).quarterly_income_stmt
