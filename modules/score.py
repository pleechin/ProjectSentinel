from __future__ import annotations

from config import (
    MAX_ACCEPTABLE_STOP_PERCENT,
    MIN_REWARD_RISK,
)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return min(max(value, minimum), maximum)


def calculate_score(
    market: dict,
    stock: dict,
    trade_plan: dict,
) -> dict:
    """
    Calculate a transparent 0-100 confidence score.

    Weighting:
        Market: 20 points
        Trend: 30 points
        Entry quality: 30 points
        Risk quality: 20 points
    """

    market_status = str(
        market.get("Status", "UNKNOWN")
    ).upper()
    market_score = float(
        market.get("Score", 0)
    )

    trend = str(
        stock.get("Trend", "UNKNOWN")
    ).upper()
    entry_score = float(
        stock.get("Entry Score", 0)
    )
    bullish_candle = bool(
        stock.get("Bullish Candle", False)
    )
    volume_ratio = float(
        stock.get("Volume Ratio", 0)
    )
    distance_from_ema20 = float(
        stock.get("EMA20 Distance %", 0)
    )

    reward_risk = float(
        trade_plan.get("Reward Risk", 0)
    )
    stop_distance_percent = float(
        trade_plan.get("Stop Distance %", 0)
    )
    position_size = int(
        trade_plan.get("Position Size", 0)
    )

    positive_factors: list[str] = []
    warnings: list[str] = []
    next_actions: list[str] = []

    market_component = round(
        _clamp(market_score, 0, 100) * 0.20
    )

    if market_status == "HEALTHY":
        positive_factors.append(
            "The wider US market is healthy"
        )
    elif market_status == "CAUTION":
        warnings.append(
            "The wider US market is in caution"
        )
        next_actions.append(
            "Use extra selectivity while the market is in caution"
        )
    elif market_status == "UNHEALTHY":
        warnings.append(
            "The wider US market does not support new long trades"
        )
        next_actions.append(
            "Wait for the wider market to improve"
        )
    else:
        warnings.append(
            "Market condition is unknown"
        )

    if trend == "STRONG BULLISH":
        trend_component = 30
        positive_factors.append(
            "The stock trend is strongly bullish"
        )
    elif trend == "BULLISH":
        trend_component = 25
        positive_factors.append(
            "The stock trend is bullish"
        )
    elif trend == "MIXED":
        trend_component = 10
        warnings.append(
            "The stock trend is mixed"
        )
        next_actions.append(
            "Wait for clearer bullish trend alignment"
        )
    else:
        trend_component = 0
        warnings.append(
            "The stock trend is bearish or unconfirmed"
        )
        next_actions.append(
            "Wait until the trend becomes bullish"
        )

    entry_component = round(
        _clamp(entry_score, 0, 100) * 0.30
    )

    if -1.0 <= distance_from_ema20 <= 2.0:
        positive_factors.append(
            "Price is close to EMA20"
        )
    elif distance_from_ema20 > 2.0:
        warnings.append(
            "Price may be extended above EMA20"
        )
        next_actions.append(
            "Wait for a pullback toward EMA20"
        )
    else:
        warnings.append(
            "Price is below the preferred EMA20 area"
        )
        next_actions.append(
            "Wait for price to recover above EMA20"
        )

    if bullish_candle:
        positive_factors.append(
            "The latest daily candle is bullish"
        )
    else:
        warnings.append(
            "The latest daily candle is not bullish"
        )
        next_actions.append(
            "Wait for bullish candle confirmation"
        )

    if volume_ratio >= 1.20:
        positive_factors.append(
            f"Volume is {volume_ratio:.2f}x its 20-day average"
        )
    else:
        warnings.append(
            "Volume confirmation is weak"
        )
        next_actions.append(
            "Wait for stronger buying volume"
        )

    risk_component = 0

    if reward_risk >= 3.0:
        risk_component += 12
        positive_factors.append(
            "Reward-to-risk is at least 3R"
        )
    elif reward_risk >= MIN_REWARD_RISK:
        risk_component += 10
        positive_factors.append(
            f"Reward-to-risk meets the "
            f"{MIN_REWARD_RISK:.1f}R minimum"
        )
    else:
        warnings.append(
            f"Reward-to-risk is below "
            f"{MIN_REWARD_RISK:.1f}R"
        )
        next_actions.append(
            "Wait for a lower entry or a clearer upside target"
        )

    if (
        0 < stop_distance_percent
        <= MAX_ACCEPTABLE_STOP_PERCENT
    ):
        risk_component += 5
        positive_factors.append(
            "Stop distance is within the accepted limit"
        )
    else:
        warnings.append(
            "Stop distance is too wide or invalid"
        )
        next_actions.append(
            "Wait for a tighter and more logical stop level"
        )

    if position_size >= 1:
        risk_component += 3
        positive_factors.append(
            "Position size fits the account risk limit"
        )
    else:
        warnings.append(
            "Account risk does not permit one full share"
        )
        next_actions.append(
            "Skip the trade or wait for a lower-risk setup"
        )

    total_score = int(
        market_component
        + trend_component
        + entry_component
        + risk_component
    )

    if total_score >= 85:
        confidence = "VERY HIGH"
        health = "EXCELLENT"
        rating = "★★★★★"
    elif total_score >= 70:
        confidence = "HIGH"
        health = "GOOD"
        rating = "★★★★☆"
    elif total_score >= 55:
        confidence = "MEDIUM"
        health = "AVERAGE"
        rating = "★★★☆☆"
    elif total_score >= 40:
        confidence = "LOW"
        health = "WEAK"
        rating = "★★☆☆☆"
    else:
        confidence = "VERY LOW"
        health = "POOR"
        rating = "★☆☆☆☆"

    return {
        "Score": total_score,
        "Confidence": confidence,
        "Health": health,
        "Rating": rating,
        "Market Component": market_component,
        "Trend Component": trend_component,
        "Entry Component": entry_component,
        "Risk Component": risk_component,
        "Positive Factors": positive_factors,
        "Warnings": warnings,
        "Next Action": list(
            dict.fromkeys(next_actions)
        ),
    }
