from __future__ import annotations

from config import MAX_ACCEPTABLE_STOP_PERCENT, MIN_REWARD_RISK


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return min(max(value, minimum), maximum)


def calculate_score(market: dict, stock: dict, trade_plan: dict) -> dict:
    """Calculate the Sprint 12.4 context-aware 0-100 score."""
    positives: list[str] = []
    warnings: list[str] = []
    actions: list[str] = []

    market_score = float(market.get("Score", market.get("market_score", 0)))
    sector_score = float(stock.get("Sector Score", 50))
    industry_score = float(stock.get("Industry Score", 50))
    trend = str(stock.get("Trend", "UNKNOWN")).upper()
    bullish = bool(stock.get("Bullish Candle", False))
    distance = float(stock.get("EMA20 Distance %", 0))
    volume_ratio = float(stock.get("Volume Ratio", 0))
    reward_risk = float(trade_plan.get("Reward Risk", 0))
    stop_pct = float(trade_plan.get("Stop Distance %", 0))
    position_size = int(trade_plan.get("Position Size", 0))

    market_component = round(_clamp(market_score, 0, 100) * 0.15)
    sector_component = round(_clamp(sector_score, 0, 100) * 0.15)
    industry_component = round(_clamp(industry_score, 0, 100) * 0.15)

    if market_score >= 70: positives.append("The broad market supports long setups")
    elif market_score < 45:
        warnings.append("The broad market is defensive")
        actions.append("Preserve capital until market conditions improve")

    if stock.get("Sector Name"):
        if sector_score >= 60: positives.append(f"{stock['Sector Name']} sector is strong ({sector_score:.0f}/100)")
        elif sector_score < 40:
            warnings.append(f"{stock['Sector Name']} sector is weak")
            actions.append("Prefer a stronger sector")
    if stock.get("Industry Name"):
        if industry_score >= 60: positives.append(f"{stock['Industry Name']} industry is strong ({industry_score:.0f}/100)")
        elif industry_score < 40:
            warnings.append(f"{stock['Industry Name']} industry is weak")
            actions.append("Wait for industry leadership to improve")

    trend_component = {"STRONG BULLISH": 20, "BULLISH": 17, "MIXED": 7}.get(trend, 0)
    if trend_component >= 17: positives.append(f"Trend is {trend.lower()}")
    else:
        warnings.append("Trend is not fully bullish")
        actions.append("Wait for bullish EMA alignment")

    momentum_component = 0
    if bullish:
        momentum_component += 5
        positives.append("Latest daily candle is bullish")
    else:
        warnings.append("Latest candle lacks bullish confirmation")
    if -1.0 <= distance <= 2.0:
        momentum_component += 5
        positives.append("Price is in the preferred EMA20 area")
    elif distance > 2.0:
        momentum_component += 2
        warnings.append("Price is extended above EMA20")
        actions.append("Wait for a pullback toward EMA20")
    else:
        warnings.append("Price is below the preferred EMA20 area")

    volume_component = round(_clamp(volume_ratio / 1.5, 0, 1) * 10)
    if volume_ratio >= 1.2: positives.append(f"Volume confirms demand at {volume_ratio:.2f}x average")
    else:
        warnings.append("Volume confirmation is weak")
        actions.append("Wait for stronger buying volume")

    risk_component = 0
    if reward_risk >= 3: risk_component += 8
    elif reward_risk >= MIN_REWARD_RISK: risk_component += 6
    else:
        warnings.append(f"Reward-to-risk is below {MIN_REWARD_RISK:.1f}R")
        actions.append("Seek a better entry or target")
    if 0 < stop_pct <= MAX_ACCEPTABLE_STOP_PERCENT: risk_component += 4
    else: warnings.append("Stop distance is too wide or invalid")
    if position_size >= 1: risk_component += 3
    else: warnings.append("Position size is not viable under the account risk limit")
    if risk_component >= 10: positives.append("The trade plan fits the risk rules")

    total = int(market_component + sector_component + industry_component + trend_component + momentum_component + volume_component + risk_component)
    if total >= 85: confidence, health, rating = "VERY HIGH", "EXCELLENT", "★★★★★"
    elif total >= 70: confidence, health, rating = "HIGH", "GOOD", "★★★★☆"
    elif total >= 55: confidence, health, rating = "MEDIUM", "AVERAGE", "★★★☆☆"
    elif total >= 40: confidence, health, rating = "LOW", "WEAK", "★★☆☆☆"
    else: confidence, health, rating = "VERY LOW", "POOR", "★☆☆☆☆"

    return {
        "Score": total, "Confidence": confidence, "Health": health, "Rating": rating,
        "Market Component": market_component, "Sector Component": sector_component,
        "Industry Component": industry_component, "Trend Component": trend_component,
        "Momentum Component": momentum_component, "Volume Component": volume_component,
        "Entry Component": momentum_component + volume_component,
        "Risk Component": risk_component, "Positive Factors": positives,
        "Warnings": warnings, "Next Action": list(dict.fromkeys(actions)),
    }
