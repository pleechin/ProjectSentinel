from config import (
    MAX_ACCEPTABLE_STOP_PERCENT,
    MIN_REWARD_RISK,
)


def evaluate_trade(
    market: dict,
    stock: dict,
    trade_plan: dict,
) -> dict:
    """
    Combine market health, stock analysis, and risk information
    into one clear trading decision.
    """

    # ========================================================
    # Read market information
    # ========================================================

    market_status = market.get("Status", "UNKNOWN")
    market_permission = bool(
        market.get("Permission", False)
    )
    market_score = float(
        market.get("Score", 0)
    )

    # ========================================================
    # Read stock information
    # ========================================================

    trend = stock.get("Trend", "UNKNOWN")

    entry_score = int(
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

    # ========================================================
    # Read trade-plan information
    # ========================================================

    reward_risk = float(
        trade_plan.get("Reward Risk", 0)
    )

    stop_distance_percent = float(
        trade_plan.get("Stop Distance %", 0)
    )

    position_size = int(
        trade_plan.get("Position Size", 0)
    )

    risk_passes = bool(
        trade_plan.get("Risk Passes", False)
    )

    # ========================================================
    # Prepare scoring and explanations
    # ========================================================

    market_component = 0
    trend_component = 0
    entry_component = 0
    risk_component = 0

    positive_factors = []
    warnings = []
    next_action = []

    # ========================================================
    # Market component: maximum 20 points
    # ========================================================

    market_component = round(
        min(
            max(market_score, 0),
            100,
        )
        * 0.20
    )

    if market_status == "HEALTHY":
        positive_factors.append(
            "The wider US market is healthy"
        )

    elif market_status == "CAUTION":
        warnings.append(
            "The wider US market is in caution"
        )

    elif market_status == "UNHEALTHY":
        warnings.append(
            "The wider US market does not support new long trades"
        )
        next_action.append(
            "Wait for the wider market to improve"
        )

    else:
        warnings.append(
            "Market condition is unknown"
        )

    # ========================================================
    # Trend component: maximum 30 points
    # ========================================================

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
        next_action.append(
            "Wait for clearer bullish trend alignment"
        )

    else:
        trend_component = 0
        warnings.append(
            "The stock trend is bearish"
        )
        next_action.append(
            "Wait until the trend becomes bullish"
        )

    # ========================================================
    # Entry component: maximum 30 points
    # ========================================================

    entry_component = round(
        min(
            max(entry_score, 0),
            100,
        )
        * 0.30
    )

    if -1.0 <= distance_from_ema20 <= 2.0:
        positive_factors.append(
            "Price is close to EMA20"
        )

    elif distance_from_ema20 > 2.0:
        warnings.append(
            "Price may be extended above EMA20"
        )
        next_action.append(
            "Wait for a pullback toward EMA20"
        )

    else:
        warnings.append(
            "Price is below the preferred EMA20 area"
        )
        next_action.append(
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
        next_action.append(
            "Wait for bullish candle confirmation"
        )

    if volume_ratio >= 1.20:
        positive_factors.append(
            "Volume is above its 20-day average"
        )

    else:
        warnings.append(
            "Volume confirmation is weak"
        )
        next_action.append(
            "Wait for stronger buying volume"
        )

    # ========================================================
    # Risk component: maximum 20 points
    # ========================================================

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
        next_action.append(
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
        next_action.append(
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
        next_action.append(
            "Skip the trade or wait for a lower-risk setup"
        )

    # ========================================================
    # Total score and health classification
    # ========================================================

    total_score = (
        market_component
        + trend_component
        + entry_component
        + risk_component
    )

    if total_score >= 85:
        health = "EXCELLENT"
        rating = "★★★★★"

    elif total_score >= 70:
        health = "GOOD"
        rating = "★★★★☆"

    elif total_score >= 55:
        health = "AVERAGE"
        rating = "★★★☆☆"

    elif total_score >= 40:
        health = "WEAK"
        rating = "★★☆☆☆"

    else:
        health = "POOR"
        rating = "★☆☆☆☆"

    # ========================================================
    # Final decision
    # ========================================================

    candidate_passes = (
        market_permission
        and market_status == "HEALTHY"
        and trend in [
            "BULLISH",
            "STRONG BULLISH",
        ]
        and entry_score >= 80
        and risk_passes
        and total_score >= 75
    )

    watch_passes = (
        market_permission
        and trend in [
            "BULLISH",
            "STRONG BULLISH",
            "MIXED",
        ]
        and total_score >= 55
    )

    if candidate_passes:
        decision = "CANDIDATE"

        if not next_action:
            next_action.append(
                "Review the chart and confirm the entry trigger"
            )
        else:
            next_action.insert(
                0,
                "Review the chart and confirm the entry trigger"
            )

        advice = (
            "This is one of today's stronger setups. "
            "Review the chart carefully and wait for the planned "
            "entry trigger before taking any position."
        )

    elif watch_passes:
        decision = "WATCH"

        if not next_action:
            next_action.append(
                "Continue monitoring for stronger confirmation"
            )

        advice = (
            "Keep this stock on your watchlist. "
            "The setup has some positive qualities, but it still "
            "needs better confirmation before entry."
        )

    else:
        decision = "WAIT"

        if not next_action:
            next_action.append(
                "Do not open a new long position"
            )

        advice = (
            "Skip this stock today. "
            "Capital is better preserved for a clearer and "
            "higher-quality opportunity."
        )

    # Remove duplicated next actions while preserving order
    next_action = list(
        dict.fromkeys(next_action)
    )

    # ========================================================
    # Return the completed decision
    # ========================================================

    return {
        "Decision": decision,
        "Health": health,
        "Rating": rating,
        "Advice": advice,

        "Total Score": total_score,

        "Market Component": market_component,
        "Trend Component": trend_component,
        "Entry Component": entry_component,
        "Risk Component": risk_component,

        "Positive Factors": positive_factors,
        "Warnings": warnings,
        "Next Action": next_action,
    }