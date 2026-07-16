import pandas as pd
import yfinance as yf

from config import ATR_PERIOD, MARKET_INDEX


def prepare_market_history(symbol: str) -> pd.DataFrame | None:
    """Download and prepare market ETF data."""

    try:
        history = yf.Ticker(symbol).history(
            period="1y",
            interval="1d",
        )

        if history.empty:
            print(f"{symbol}: No market data returned")
            return None

        history = history.dropna(
            subset=["Open", "High", "Low", "Close", "Volume"]
        ).copy()

        if len(history) < 60:
            print(f"{symbol}: Not enough historical data")
            return None

        history["EMA20"] = history["Close"].ewm(
            span=20,
            adjust=False,
        ).mean()

        history["EMA50"] = history["Close"].ewm(
            span=50,
            adjust=False,
        ).mean()

        history["EMA200"] = history["Close"].ewm(
            span=200,
            adjust=False,
        ).mean()

        previous_close = history["Close"].shift(1)

        true_range = pd.concat(
            [
                history["High"] - history["Low"],
                (history["High"] - previous_close).abs(),
                (history["Low"] - previous_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

        history["ATR14"] = true_range.ewm(
            alpha=1 / ATR_PERIOD,
            adjust=False,
        ).mean()

        return history

    except Exception as error:
        print(f"{symbol}: Market data error — {error}")
        return None


def analyse_market() -> dict:
    """
    Analyse SPY and QQQ and return overall US market health.
    """

    market_results = []
    total_score = 0

    for symbol in MARKET_INDEX:
        history = prepare_market_history(symbol)

        if history is None:
            continue

        latest = history.iloc[-1]
        previous = history.iloc[-6]

        close_price = float(latest["Close"])
        ema20 = float(latest["EMA20"])
        ema50 = float(latest["EMA50"])
        ema200 = float(latest["EMA200"])
        previous_ema50 = float(previous["EMA50"])

        score = 0
        reasons = []

        if close_price > ema20:
            score += 25
            reasons.append("Price above EMA20")
        else:
            reasons.append("Price below EMA20")

        if ema20 > ema50:
            score += 25
            reasons.append("EMA20 above EMA50")
        else:
            reasons.append("EMA20 below EMA50")

        if close_price > ema200:
            score += 25
            reasons.append("Price above EMA200")
        else:
            reasons.append("Price below EMA200")

        if ema50 > previous_ema50:
            score += 25
            reasons.append("EMA50 rising")
        else:
            reasons.append("EMA50 flat or falling")

        total_score += score

        market_results.append(
            {
                "Symbol": symbol,
                "Close": close_price,
                "EMA20": ema20,
                "EMA50": ema50,
                "EMA200": ema200,
                "Score": score,
                "Reasons": ", ".join(reasons),
            }
        )

    if not market_results:
        return {
            "Score": 0,
            "Status": "UNKNOWN",
            "Permission": False,
            "Results": [],
        }

    maximum_score = len(market_results) * 100
    market_score = (total_score / maximum_score) * 100

    if market_score >= 75:
        status = "HEALTHY"
        permission = True
    elif market_score >= 50:
        status = "CAUTION"
        permission = True
    else:
        status = "UNHEALTHY"
        permission = False

    return {
        "Score": market_score,
        "Status": status,
        "Permission": permission,
        "Results": market_results,
    }