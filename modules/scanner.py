import pandas as pd
import yfinance as yf

from config import (
    ASSET_UNIVERSE,
    ATR_PERIOD,
    EMA20,
    EMA50,
    EMA200,
    MIN_VOLUME_RATIO,
    WATCHLIST_SYMBOLS,
)
from indicators.atr import add_atr
from indicators.ema import add_ema
from indicators.volume import add_average_volume
from modules.context_mapping import lookup_context_score, resolve_asset_context
from modules.decision import evaluate_trade
from modules.ranking import rank_opportunities
from modules.risk import calculate_trade_plan


def load_history(symbol: str) -> pd.DataFrame | None:
    """Download and clean one year of daily stock or ETF data."""
    try:
        history = yf.Ticker(symbol).history(period="1y", interval="1d")
        if history.empty:
            print(f"{symbol}: No data returned")
            return None
        history = history.dropna(subset=["Open", "High", "Low", "Close", "Volume"]).copy()
        if len(history) < EMA200:
            print(f"{symbol}: Not enough historical data")
            return None
        return history
    except Exception as error:
        print(f"{symbol}: Data error — {error}")
        return None


def calculate_indicators(history: pd.DataFrame) -> pd.DataFrame:
    """Add all indicators needed by the scanner."""
    result = add_ema(history, periods=(EMA20, EMA50, EMA200))
    result = add_atr(result, period=ATR_PERIOD)
    return add_average_volume(result, period=20)


def analyse_stock_setup(symbol: str, history: pd.DataFrame) -> dict:
    """Calculate technical setup values for a stock or ETF."""
    latest = history.iloc[-1]
    open_price = float(latest["Open"])
    close_price = float(latest["Close"])
    ema20 = float(latest[f"EMA{EMA20}"])
    ema50 = float(latest[f"EMA{EMA50}"])
    ema200 = float(latest[f"EMA{EMA200}"])
    volume = float(latest["Volume"])
    average_volume = float(latest["AvgVolume20"])

    distance_from_ema20 = ((close_price - ema20) / ema20) * 100
    volume_ratio = volume / average_volume if average_volume > 0 else 0
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
        entry_reasons.append(f"Volume is at least {MIN_VOLUME_RATIO:.2f}x average")

    metadata = ASSET_UNIVERSE.get(
        symbol,
        {"Asset Type": "STOCK", "Category": "Unclassified"},
    )

    return {
        "Symbol": symbol,
        "Asset Type": metadata["Asset Type"],
        "Category": metadata["Category"],
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


def scan_stock(symbol: str, market: dict, sectors: dict | None = None, industries: dict | None = None) -> dict | None:
    """Run the full Sentinel analysis for one tradable stock or ETF."""
    history = load_history(symbol)
    if history is None:
        return None
    history = calculate_indicators(history)
    asset = analyse_stock_setup(symbol=symbol, history=history)
    sector_name, industry_name = resolve_asset_context(symbol, str(asset.get("Category", "")))
    sector_score, sector_status = lookup_context_score(sectors, sector_name, "Sector", "Sector Score")
    industry_score, industry_status = lookup_context_score(industries, industry_name, "Industry", "Industry Score")
    asset.update({
        "Sector Name": sector_name, "Sector Score": sector_score, "Sector Status": sector_status,
        "Industry Name": industry_name, "Industry Score": industry_score, "Industry Status": industry_status,
    })
    trade_plan = calculate_trade_plan(history)
    decision = evaluate_trade(market=market, stock=asset, trade_plan=trade_plan)
    return {**asset, **trade_plan, **decision}


def scan_watchlist(market: dict, sectors: dict | None = None, industries: dict | None = None) -> pd.DataFrame:
    """Scan stocks and ETFs and return one ranked opportunity table."""
    results = []
    for symbol in WATCHLIST_SYMBOLS:
        metadata = ASSET_UNIVERSE.get(symbol, {})
        asset_type = metadata.get("Asset Type", "ASSET")
        print(f"Scanning {symbol} ({asset_type})...")
        result = scan_stock(symbol=symbol, market=market, sectors=sectors, industries=industries)
        if result is not None:
            results.append(result)
    return rank_opportunities(results)
