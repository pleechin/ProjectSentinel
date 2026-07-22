"""Industry-leadership analysis for Project Sentinel.

Sprint 12.3 ranks industry and thematic ETFs by trend and relative strength
versus SPY. It does not yet modify individual stock scores; that integration
belongs to Sprint 12.4.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

from watchlists.industry_etfs import (
    INDUSTRY_BENCHMARK,
    INDUSTRY_ETFS,
    INDUSTRY_LOOKBACK_MEDIUM,
    INDUSTRY_LOOKBACK_SHORT,
)

HistoryLoader = Callable[[str], pd.DataFrame | None]


def download_industry_history(symbol: str) -> pd.DataFrame | None:
    """Download one year of daily history for an industry ETF or benchmark."""
    try:
        import yfinance as yf

        history = yf.Ticker(symbol).history(period="1y", interval="1d")
        if history.empty or "Close" not in history.columns:
            return None
        history = history.dropna(subset=["Close"]).copy()
        if len(history) <= INDUSTRY_LOOKBACK_MEDIUM:
            return None
        return history
    except Exception as error:
        print(f"{symbol}: Industry data error — {error}")
        return None


def _return_percent(history: pd.DataFrame, periods: int) -> float:
    latest = float(history["Close"].iloc[-1])
    previous = float(history["Close"].iloc[-(periods + 1)])
    return ((latest / previous) - 1.0) * 100.0 if previous else 0.0


def _analyse_industry(
    industry: str,
    symbol: str,
    history: pd.DataFrame,
    benchmark_short: float,
    benchmark_medium: float,
) -> dict[str, Any]:
    close = float(history["Close"].iloc[-1])
    ema20 = float(history["Close"].ewm(span=20, adjust=False).mean().iloc[-1])
    ema50 = float(history["Close"].ewm(span=50, adjust=False).mean().iloc[-1])
    short_return = _return_percent(history, INDUSTRY_LOOKBACK_SHORT)
    medium_return = _return_percent(history, INDUSTRY_LOOKBACK_MEDIUM)
    relative_short = short_return - benchmark_short
    relative_medium = medium_return - benchmark_medium

    score = 0
    reasons: list[str] = []
    if close > ema20:
        score += 20
        reasons.append("Price above EMA20")
    if close > ema50:
        score += 20
        reasons.append("Price above EMA50")
    if ema20 > ema50:
        score += 20
        reasons.append("EMA20 above EMA50")
    if relative_short > 0:
        score += 20
        reasons.append("Outperforming SPY over 1 month")
    if relative_medium > 0:
        score += 20
        reasons.append("Outperforming SPY over 3 months")

    if score >= 80:
        status = "LEADING"
    elif score >= 60:
        status = "STRONG"
    elif score >= 40:
        status = "NEUTRAL"
    else:
        status = "WEAK"

    return {
        "Industry": industry,
        "Symbol": symbol,
        "Close": close,
        "EMA20": ema20,
        "EMA50": ema50,
        "1M Return %": short_return,
        "3M Return %": medium_return,
        "1M Relative %": relative_short,
        "3M Relative %": relative_medium,
        "Industry Score": score,
        "Status": status,
        "Reasons": "; ".join(reasons) if reasons else "No leadership conditions met",
    }


def get_industry_leadership(
    history_loader: HistoryLoader = download_industry_history,
) -> dict[str, Any]:
    """Rank industry ETFs and return a dashboard-friendly snapshot."""
    benchmark = history_loader(INDUSTRY_BENCHMARK)
    if benchmark is None or benchmark.empty:
        return {
            "status": "NO_DATA",
            "benchmark": INDUSTRY_BENCHMARK,
            "leaders": [],
            "laggards": [],
            "rankings": [],
            "message": "SPY benchmark data unavailable.",
        }

    benchmark_short = _return_percent(benchmark, INDUSTRY_LOOKBACK_SHORT)
    benchmark_medium = _return_percent(benchmark, INDUSTRY_LOOKBACK_MEDIUM)
    rankings: list[dict[str, Any]] = []

    for industry, symbol in INDUSTRY_ETFS.items():
        history = history_loader(symbol)
        if history is None or history.empty:
            rankings.append({
                "Industry": industry,
                "Symbol": symbol,
                "Close": None,
                "EMA20": None,
                "EMA50": None,
                "1M Return %": None,
                "3M Return %": None,
                "1M Relative %": None,
                "3M Relative %": None,
                "Industry Score": 0,
                "Status": "NO DATA",
                "Reasons": "Industry data unavailable",
            })
            continue
        rankings.append(
            _analyse_industry(
                industry,
                symbol,
                history,
                benchmark_short,
                benchmark_medium,
            )
        )

    rankings.sort(
        key=lambda item: (
            int(item.get("Industry Score", 0)),
            float(item.get("3M Relative %") or -999.0),
            float(item.get("1M Relative %") or -999.0),
        ),
        reverse=True,
    )
    for rank, item in enumerate(rankings, start=1):
        item["Rank"] = rank

    available = [item for item in rankings if item["Status"] != "NO DATA"]
    leaders = available[:3]
    laggards = available[-3:][::-1] if available else []

    return {
        "status": "READY" if available else "NO_DATA",
        "benchmark": INDUSTRY_BENCHMARK,
        "benchmark_1m_return": benchmark_short,
        "benchmark_3m_return": benchmark_medium,
        "leaders": leaders,
        "laggards": laggards,
        "rankings": rankings,
        "message": f"Ranked {len(available)} of {len(INDUSTRY_ETFS)} industries.",
    }
