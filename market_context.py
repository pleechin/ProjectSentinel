"""Project Sentinel market-context engine.

The public function :func:`get_market_context` returns both a new, descriptive
API and the legacy keys already consumed by Sentinel's decision and dashboard
modules. This lets the market engine improve without breaking existing code.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

from watchlists.market import (
    MARKET_SYMBOLS,
    TREND_SYMBOLS,
    VIX_RISK_ON_LEVEL,
    VOLATILITY_SYMBOL,
)

HistoryLoader = Callable[[str], pd.DataFrame | None]


def download_market_history(symbol: str) -> pd.DataFrame | None:
    """Download one year of daily history and calculate EMA50."""
    try:
        import yfinance as yf

        history = yf.Ticker(symbol).history(period="1y", interval="1d")
        if history.empty or "Close" not in history.columns:
            return None

        history = history.dropna(subset=["Close"]).copy()
        if len(history) < 55:
            return None

        history["EMA50"] = history["Close"].ewm(span=50, adjust=False).mean()
        return history
    except Exception as error:  # Network/provider errors must not crash a scan.
        print(f"{symbol}: Market context data error — {error}")
        return None


def _trend_result(symbol: str, history: pd.DataFrame) -> dict[str, Any]:
    latest = history.iloc[-1]
    close = float(latest["Close"])
    ema50 = float(latest["EMA50"])
    bullish = close > ema50
    return {
        "Symbol": symbol,
        "Name": MARKET_SYMBOLS[symbol],
        "Close": close,
        "EMA50": ema50,
        "Score": 20 if bullish else 0,
        "Signal": "BULLISH" if bullish else "BEARISH",
        "Reasons": "Price above EMA50" if bullish else "Price below EMA50",
    }


def _vix_result(history: pd.DataFrame) -> dict[str, Any]:
    close = float(history.iloc[-1]["Close"])
    risk_on = close < VIX_RISK_ON_LEVEL
    return {
        "Symbol": VOLATILITY_SYMBOL,
        "Name": MARKET_SYMBOLS[VOLATILITY_SYMBOL],
        "Close": close,
        "EMA50": None,
        "Score": 20 if risk_on else 0,
        "Signal": "LOW" if risk_on else "ELEVATED",
        "Reasons": (
            f"VIX below {VIX_RISK_ON_LEVEL:.0f}"
            if risk_on
            else f"VIX at or above {VIX_RISK_ON_LEVEL:.0f}"
        ),
    }


def get_market_context(history_loader: HistoryLoader = download_market_history) -> dict[str, Any]:
    """Return a 0–100 market-health assessment.

    Scoring (20 points each): SPY, QQQ and IWM above EMA50; VIX below 20;
    and trend alignment when at least two of the three equity ETFs are bullish.
    Missing data receives no points and is reported explicitly.
    """
    results: list[dict[str, Any]] = []
    bullish_trends = 0
    score = 0

    for symbol in TREND_SYMBOLS:
        history = history_loader(symbol)
        if history is None or history.empty:
            results.append({
                "Symbol": symbol,
                "Name": MARKET_SYMBOLS[symbol],
                "Close": None,
                "EMA50": None,
                "Score": 0,
                "Signal": "NO DATA",
                "Reasons": "Market data unavailable",
            })
            continue
        item = _trend_result(symbol, history)
        results.append(item)
        score += int(item["Score"])
        bullish_trends += int(item["Signal"] == "BULLISH")

    vix_history = history_loader(VOLATILITY_SYMBOL)
    if vix_history is None or vix_history.empty:
        results.append({
            "Symbol": VOLATILITY_SYMBOL,
            "Name": MARKET_SYMBOLS[VOLATILITY_SYMBOL],
            "Close": None,
            "EMA50": None,
            "Score": 0,
            "Signal": "NO DATA",
            "Reasons": "Market data unavailable",
        })
    else:
        vix_item = _vix_result(vix_history)
        results.append(vix_item)
        score += int(vix_item["Score"])

    aligned = bullish_trends >= 2
    if aligned:
        score += 20

    if score >= 80:
        status, confidence, permission = "BULLISH", "HIGH", True
    elif score >= 60:
        status, confidence, permission = "NEUTRAL", "MEDIUM", True
    else:
        status, confidence, permission = "DEFENSIVE", "LOW", False

    details = {item["Symbol"]: item["Signal"] for item in results}
    details["TREND_ALIGNMENT"] = "ALIGNED" if aligned else "NOT ALIGNED"

    return {
        # New descriptive API.
        "market_score": score,
        "market_status": status,
        "market_confidence": confidence,
        "details": details,
        "drivers": results,
        # Backward-compatible API used by existing Sentinel modules.
        "Score": float(score),
        "Status": status,
        "Confidence": confidence,
        "Permission": permission,
        "Results": results,
    }


def analyse_market() -> dict[str, Any]:
    """Backward-compatible name retained for existing imports."""
    return get_market_context()
