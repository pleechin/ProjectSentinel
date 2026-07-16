import pandas as pd
import yfinance as yf

from config import (
    ATR_PERIOD,
    EMA20,
    EMA50,
    EMA200,
    MIN_VOLUME_RATIO,
    WATCHLIST,
)
from indicators.atr import add_atr
from indicators.ema import add_ema
from indicators.volume import add_average_volume
from modules.decision import evaluate_trade
from modules.risk import calculate_trade_plan


def load_history(symbol: str) -> pd.DataFrame | None:
    """Download and clean one year of daily stock data."""

    try:
        history = yf.Ticker(symbol).history(
            period="1y",
            interval="1d",
        )

        if history.empty:
            print(f"{symbol}: No data returned")
            return None

        history = history.dropna(
            subset=["Open", "High", "Low", "Close", "Volume"]
        ).copy()

        if len(history) < EMA200:
            print(f"{symbol}: Not enough historical data")
            return None

        return history

    except Exception as error:
        print(f"{symbol}: Data error — {error}")
        return None


def calculate_indicators(
    history: pd.DataFrame,
) -> pd.DataFrame:
    """Add all indicators needed by the scanner."""

    result = add_ema(
        history,
        periods=(EMA20, EMA50, EMA200),
    )

    result = add_atr(
        result,
        period=ATR_PERIOD,
    )

    result = add_average_volume(
        result,
        period=20,
    )

    return result


def analyse_stock_setup(
    symbol: str,
    history: pd.DataFrame,
) -> dict:
    """Calculate trend, candle, volume and entry score."""

    latest = history.iloc[-1]

    open_price = float(latest["Open"])
    close_price = float(latest["Close"])

    ema20 = float(latest[f"EMA{EMA20}"])
    ema50 = float(latest[f"EMA{EMA50}"])
    ema200 = float(latest[f"EMA{EMA200}"])

    volume = float(latest["Volume"])
    average_volume = float(latest["AverageVolume20"])

    distance_from_ema20 = (
        (close_price - ema20) / ema20
    ) * 100

    volume_ratio = (
        volume / average_volume
        if average_volume > 0
        else 0
    )

    bullish_candle = close_price > open_price

    if close_price > ema20 > ema50 > ema200:
        trend = "STRONG BULLISH"
    elif close_price > ema20 > ema50:
        trend = "BULLISH"
    elif close_price < ema20 < ema50:
        trend = "BEARISH"
    else:
        trend = "MIXED"

    entry_score = 0
    entry_reasons = []

    if trend in ["BULLISH", "STRONG BULLISH"]:
        entry_score += 40
        entry_reasons.append("Bullish EMA trend")

    if -1.0 <= distance_from_ema20 <= 2.0:
        entry_score += 25
        entry_reasons.append("Price is near EMA20")

    if bullish_candle:
        entry_score += 15
        entry_reasons.append("Latest daily candle is bullish")

    if volume_ratio >= MIN_VOLUME_RATIO:
        entry_score += 20
        entry_reasons.append(
            f"Volume is at least {MIN_VOLUME_RATIO:.2f}x average"
        )

    return {
        "Symbol": symbol,
        "Data Date": history.index[-1].date(),
        "Close": close_price,
        "EMA20": ema20,
        "EMA50": ema50,
        "EMA200": ema200,
        "Trend": trend,
        "Bullish Candle": bullish_candle,
        "Volume Ratio": volume_ratio,
        "EMA20 Distance %": distance_from_ema20,
        "Entry Score": entry_score,
        "Entry Reasons": entry_reasons,
    }


def scan_stock(
    symbol: str,
    market: dict,
) -> dict | None:
    """Run the full Sentinel analysis for one stock."""

    history = load_history(symbol)

    if history is None:
        return None

    history = calculate_indicators(history)

    stock = analyse_stock_setup(
        symbol=symbol,
        history=history,
    )

    trade_plan = calculate_trade_plan(history)

    decision = evaluate_trade(
        market=market,
        stock=stock,
        trade_plan=trade_plan,
    )

    return {
        **stock,
        **trade_plan,
        **decision,
    }


def scan_watchlist(
    market: dict,
) -> pd.DataFrame:
    """Scan and rank all configured watchlist stocks."""

    results = []

    for symbol in WATCHLIST:
        print(f"Scanning {symbol}...")

        result = scan_stock(
            symbol=symbol,
            market=market,
        )

        if result is not None:
            results.append(result)

    if not results:
        return pd.DataFrame()

    ranking = pd.DataFrame(results)

    decision_order = {
        "CANDIDATE": 3,
        "WATCH": 2,
        "WAIT": 1,
    }

    ranking["Decision Rank"] = ranking["Decision"].map(
        decision_order
    ).fillna(0)

    ranking = ranking.sort_values(
        by=[
            "Decision Rank",
            "Total Score",
            "Reward Risk",
            "Volume Ratio",
        ],
        ascending=[
            False,
            False,
            False,
            False,
        ],
    ).reset_index(drop=True)

    return ranking