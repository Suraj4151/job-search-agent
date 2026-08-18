import os
import datetime as dt
import requests
import pandas as pd
import yfinance as yf
import ta  # technical analysis library

WATCHLIST = [
    "NVDA", "AMD", "INTC", "AVGO", "MRVL", "ARM", "BIDU",
    "ANET", "CSCO", "LITE", "COHR", "FN", "INFN",
    "MU", "WDC", "STX", "PSTG",
    "MSFT", "GOOGL", "AMZN", "ORCL", "IBM", "BABA", "TCEHY", "EQIX",
    "SNOW", "PLTR", "NOW", "CRM", "DDOG", "ESTC", "MDB", "HUBS", "ADBE",
    "VRT", "ETN", "SBGSY", "SMCI", "DELL", "NTNX", "GNRC", "PWR",
    "QCOM", "AAPL", "TSLA", "PATH", "IRBT", "NXPI", "SONY", "LNVGY",
    "ASML", "TSM", "AMAT", "LRCX", "CDNS", "SNPS", "KLAC", "GFS"
]

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def fetch_ohlcv(ticker: str, period: str = "6mo") -> pd.DataFrame:
    df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"No data for {ticker}")
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.columns = ["open", "high", "low", "close", "volume"]
    return df

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df["rsi_14"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["sma_20"] = ta.trend.SMAIndicator(df["close"], window=20).sma_indicator()
    df["sma_50"] = ta.trend.SMAIndicator(df["close"], window=50).sma_indicator()
    df["sma_200"] = ta.trend.SMAIndicator(df["close"], window=200).sma_indicator()
    return df

def latest_snapshot(df: pd.DataFrame) -> dict:
    last = df.iloc[-1]
    return {
        "price": float(last["close"]),
        "rsi_14": float(last["rsi_14"]),
        "macd": float(last["macd"]),
        "macd_signal": float(last["macd_signal"]),
        "sma_20": float(last["sma_20"]),
        "sma_50": float(last["sma_50"]),
        "sma_200": float(last["sma_200"]),
    }

def fetch_news(ticker: str, max_articles: int = 5) -> list:
    if not NEWSAPI_KEY:
        return []
    url = (
        "https://newsapi.org/v2/everything?"
        f"q={ticker}&language=en&sortBy=publishedAt&pageSize={max_articles}&apiKey={NEWSAPI_KEY}"
    )
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        return []
    data = resp.json()
    articles = data.get("articles", [])
    return [
        {
            "title": a.get("title"),
            "source": a.get("source", {}).get("name"),
            "published_at": a.get("publishedAt"),
            "url": a.get("url"),
        }
        for a in articles
    ]

def rule_based_signal(snapshot: dict) -> str:
    rsi = snapshot["rsi_14"]
    price = snapshot["price"]
    sma_50 = snapshot["sma_50"]
    sma_200 = snapshot["sma_200"]
    if rsi > 70 and price > sma_50 * 1.05:
        return "SELL"
    if rsi < 30 and price < sma_50 * 0.95 and price > sma_200:
        return "BUY"
    return "HOLD"

def analyze_ticker(ticker: str) -> dict:
    try:
        df = fetch_ohlcv(ticker)
        df = compute_indicators(df)
        snap = latest_snapshot(df)
        news = fetch_news(ticker)
        signal = rule_based_signal(snap)
        return {
            "ticker": ticker,
            "date": dt.date.today().isoformat(),
            "snapshot": snap,
            "news": news,
            "signal": signal,
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

def run_daily():
    reports = []
    for t in WATCHLIST:
        print(f"Analyzing {t}...")
        rep = analyze_ticker(t)
        reports.append(rep)
    out_name = f"daily_ai_report_{dt.date.today().isoformat()}.json"
    pd.Series(reports).to_json(out_name, orient="values", indent=2)
    print(f"Saved report to {out_name}")

if __name__ == "__main__":
    run_daily()

