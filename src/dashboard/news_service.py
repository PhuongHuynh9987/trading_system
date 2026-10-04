from datetime import datetime, timezone
import os

import requests
import yfinance as yf
from textblob import TextBlob
from dotenv import load_dotenv


load_dotenv()


NEWS_API_URL = "https://newsapi.org/v2/everything"


def _relative_time(value):
    if not value:
        return "Unknown"
    try:
        published = datetime.fromisoformat(value.replace("Z", "+00:00"))
        elapsed = datetime.now(timezone.utc) - published
        minutes = max(0, int(elapsed.total_seconds() // 60))
    except (TypeError, ValueError):
        return "Unknown"

    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    return f"{hours // 24}d ago"


def _sentiment(text):
    score = round(TextBlob(text or "").sentiment.polarity, 2)
    if score > 0.1:
        return score, "Positive"
    if score < -0.1:
        return score, "Negative"
    return score, "Neutral"


def _market_move(symbol):
    try:
        history = yf.Ticker(symbol).history(period="5d", interval="1d", auto_adjust=False)
        closes = history["Close"].dropna()
        if len(closes) < 2:
            return None
        previous = float(closes.iloc[-2])
        current = float(closes.iloc[-1])
        return round((current - previous) / previous * 100, 2) if previous else None
    except Exception:
        return None


def get_news_market_impact(symbols, limit_per_symbol=3):
    """Return current headlines, sentiment, and the latest daily price move."""
    api_key = os.getenv("newsapi_api_key")
    if not api_key:
        return [], "NewsAPI key is not configured."

    records = []
    for symbol in dict.fromkeys(symbols):
        try:
            response = requests.get(
                NEWS_API_URL,
                params={
                    "q": f'"{symbol}"',
                    "apiKey": api_key,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": limit_per_symbol,
                },
                timeout=8,
            )
            response.raise_for_status()
            articles = response.json().get("articles", [])
            move = _market_move(symbol)
            for article in articles:
                title = (article.get("title") or "").strip()
                description = (article.get("description") or "").strip()
                score, label = _sentiment(f"{title}. {description}")
                records.append({
                    "symbol": symbol,
                    "title": title or "Untitled article",
                    "source": (article.get("source") or {}).get("name") or "Unknown source",
                    "url": article.get("url"),
                    "published_at": _relative_time(article.get("publishedAt")),
                    "sentiment": label,
                    "sentiment_score": score,
                    "market_move": move,
                })
        except (requests.RequestException, ValueError) as error:
            return records, f"News unavailable for {symbol}: {error}"

    return records, None