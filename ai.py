import json
from openai import OpenAI


def run_ai_debate(ticker, news_texts, fund, api_key, language="English"):
    """Run 6-investor debate + portfolio manager verdict. Returns parsed JSON dict."""
    fund_text = "Key financial data:\n" + "\n".join(
        f"- {k}: {v}" for k, v in fund.items() if v != "N/A"
    )
    lang_instruction = (
        "Write all reasoning, action, and rationale fields in Korean (한국어)."
        if language == "한국어" else
        "Write all reasoning, action, and rationale fields in English."
    )
    prompt = f"""
You are simulating a live investment committee debate about '{ticker}'.
Latest news headlines:
{news_texts}

{fund_text}

{lang_instruction}

Return ONLY a valid JSON object with this exact structure (no extra text):
{{
  "Warren":  {{"signal": "BULLISH|BEARISH|NEUTRAL", "confidence": <1-100>, "reasoning": "<2-3 sentences from Warren Buffett's value-investing perspective>"}},
  "Charlie": {{"signal": "BULLISH|BEARISH|NEUTRAL", "confidence": <1-100>, "reasoning": "<2-3 sentences from Charlie Munger's mental-models perspective>"}},
  "Michael": {{"signal": "BULLISH|BEARISH|NEUTRAL", "confidence": <1-100>, "reasoning": "<2-3 sentences from Michael Burry's contrarian macro perspective>"}},
  "Peter":   {{"signal": "BULLISH|BEARISH|NEUTRAL", "confidence": <1-100>, "reasoning": "<2-3 sentences from Peter Lynch's GARP perspective>"}},
  "Cathie":  {{"signal": "BULLISH|BEARISH|NEUTRAL", "confidence": <1-100>, "reasoning": "<2-3 sentences from Cathie Wood's disruptive-technology perspective>"}},
  "Bill":    {{"signal": "BULLISH|BEARISH|NEUTRAL", "confidence": <1-100>, "reasoning": "<2-3 sentences from Bill Ackman's activist-investor perspective>"}},
  "Manager": {{"verdict": "BUY|SELL|HOLD", "confidence": <1-100>, "action": "<One concrete actionable sentence>", "rationale": "<2-3 sentences synthesizing the panel's views>"}}
}}
"""
    client = OpenAI(api_key=api_key)
    resp   = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a multi-agent hedge fund simulator. Output only valid JSON."},
            {"role": "user",   "content": prompt},
        ],
    )
    return json.loads(resp.choices[0].message.content)


def run_portfolio_analysis(ticker, news, fund, api_key, language="English"):
    """Lightweight single-signal analysis for portfolio mode. Returns parsed JSON dict."""
    fund_text = "\n".join(f"- {k}: {v}" for k, v in fund.items() if v != "N/A")
    lang_note = (
        "Write the summary field in Korean (한국어)."
        if language == "한국어" else
        "Write the summary field in English."
    )
    prompt = f"""
Analyze '{ticker}' as a portfolio manager.
News: {news[:500]}
Financials: {fund_text}
{lang_note}
Return JSON: {{"signal": "BULLISH|BEARISH|NEUTRAL", "confidence": <1-100>, "summary": "<1 sentence rationale>", "verdict": "BUY|SELL|HOLD"}}
"""
    client = OpenAI(api_key=api_key)
    resp   = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Portfolio analysis. Output only valid JSON."},
            {"role": "user",   "content": prompt},
        ],
    )
    return json.loads(resp.choices[0].message.content)
