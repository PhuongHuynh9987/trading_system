import yfinance as yf


def _rsi(closes, period=14):
    changes = closes.diff().dropna()
    gains = changes.clip(lower=0)
    losses = -changes.clip(upper=0)
    average_gain = gains.rolling(period).mean().iloc[-1]
    average_loss = losses.rolling(period).mean().iloc[-1]
    if average_loss == 0:
        return 100.0 if average_gain > 0 else 50.0
    return round(100 - (100 / (1 + average_gain / average_loss)), 1)


def get_trading_recommendations(symbols, sector_by_symbol=None):
    """Build transparent technical recommendations from recent daily prices."""
    sector_by_symbol = sector_by_symbol or {}
    recommendations = []
    for symbol in dict.fromkeys(symbols):
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period="3mo", interval="1d", auto_adjust=False)
            closes = history["Close"].dropna()
            if len(closes) < 21:
                continue

            current_price = float(closes.iloc[-1])
            moving_average = float(closes.rolling(20).mean().iloc[-1])
            momentum = float((current_price / closes.iloc[-6] - 1) * 100)
            relative_strength = _rsi(closes)
            above_average = current_price >= moving_average

            if above_average and momentum > 0 and 45 <= relative_strength <= 70:
                signal = "BUY"
                reason = "Positive 5-day momentum above the 20-day average"
            elif relative_strength > 70:
                signal = "SELL"
                reason = "RSI indicates overbought conditions"
            elif not above_average or momentum < -2:
                signal = "SELL"
                reason = "Price is below trend or momentum is weakening"
            else:
                signal = "HOLD"
                reason = "Trend and momentum signals are mixed"

            strength = min(99, max(50, round(50 + abs(momentum) * 4 + abs(relative_strength - 50) * 0.35)))
            sector = sector_by_symbol.get(symbol)
            industry = None
            if not sector:
                try:
                    metadata = ticker.info
                    sector = metadata.get("sector")
                    industry = metadata.get("industry")
                except Exception:
                    sector = None
            recommendations.append({
                "symbol": symbol,
                "sector": sector or "Unknown",
                "industry": industry,
                "price": round(current_price, 2),
                "signal": signal,
                "strength": strength,
                "reason": reason,
            })
        except Exception:
            continue

    return recommendations