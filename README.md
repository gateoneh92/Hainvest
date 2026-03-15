# 👋 HaiInvestor

> **New to investing? Just pick a stock — 6 legendary AI investors will debate it for you.**

HaiInvestor is a free AI-powered stock analysis app designed for beginners. It simulates a live investment committee debate using 6 legendary investor personas, real-time price data, and live financial fundamentals.

🔗 **Live Demo:** https://ainvest-jnpzmtom62rulztvu24d6c.streamlit.app

---

## 🧠 The AI Investor Panel

| Investor | Style |
|----------|-------|
| 👴 Warren Buffett | Value Investing |
| 🧠 Charlie Munger | Mental Models |
| 🐻 Michael Burry | Contrarian / Macro |
| 🏃 Peter Lynch | Growth at Reasonable Price |
| 🚀 Cathie Wood | Disruptive Innovation |
| ⚔️ Bill Ackman | Activist Investing |

Each investor analyzes the latest news headlines and real financial data, then outputs a **BULLISH / BEARISH / NEUTRAL** signal with a conviction score. A Portfolio Manager synthesizes the panel's views into a final **BUY / SELL / HOLD** verdict.

---

## ✨ Features

### 📊 Single Stock
- Live price, daily change, day high/low
- 6-month candlestick chart
- Key fundamentals: Market Cap, P/E, Forward P/E, P/B, Revenue Growth, Profit Margin, ROE, Debt/Equity
- Full 6-agent debate with conviction bars
- Panel consensus summary with visual vote bar
- Final BUY/SELL/HOLD verdict
- One-click Share on X (Twitter)

### 💼 Portfolio Mode
- Analyze up to 6 tickers at once
- AI signal + conviction score per stock
- Suggested portfolio weights based on bullish conviction
- Allocation pie chart
- Share results on X

### 📈 AI Signal Backtest
- Simulates returns based on quarterly fundamental signals
- Signal logic: Revenue growth + profitability (same criteria our AI panel uses)
- Compares strategy return vs Buy & Hold
- Metrics: total return, max drawdown, quarters invested
- Bullish period shading on chart
- Quarterly signal breakdown table

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| AI | OpenAI GPT-4o-mini |
| Market Data | yfinance |
| News | Google News RSS |
| Charts | Plotly |
| Parsing | BeautifulSoup |

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/gateoneh92/Hainvest.git
cd Hainvest

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your OpenAI API key
mkdir -p .streamlit
echo 'OPENAI_API_KEY = "sk-..."' > .streamlit/secrets.toml

# 5. Run the app
streamlit run app.py
```

---

## ⚠️ Disclaimer

This app is a simulation for **educational purposes only**. AI analysis is based on public news headlines and financial data. This is **not financial advice**. Always do your own research before making any investment decisions.

---

## 📬 Feedback

Think the AI panel is full of garbage? [Pay $1 and insult me via PayPal](https://www.paypal.com/ncp/payment/A3Q3JEV6WRXSG). I'll read every single one.
