from __future__ import annotations

from config import MIN_REWARD_RISK


def _first(items: list[str], fallback: str) -> str:
    return items[0] if items else fallback


def build_coach_guidance(
    market: dict,
    stock: dict,
    trade_plan: dict,
    score_result: dict,
    decision: str,
) -> dict:
    """Create deterministic trading-coach guidance from Sentinel evidence.

    This module explains an existing decision. It does not change the score,
    decision, position size, entry, stop, or target.
    """

    decision = str(decision).upper()
    market_status = str(market.get("Status", "UNKNOWN")).upper()
    trend = str(stock.get("Trend", "UNKNOWN")).upper()
    confidence = str(score_result.get("Confidence", "UNKNOWN"))
    score = int(score_result.get("Score", 0))
    warnings = list(score_result.get("Warnings", []))
    next_actions = list(score_result.get("Next Action", []))

    reward_risk = float(trade_plan.get("Reward Risk", 0))
    stop_percent = float(trade_plan.get("Stop Distance %", 0))
    risk_passes = bool(trade_plan.get("Risk Passes", False))

    if decision == "CANDIDATE":
        headline = "Strong setup — prepare, but wait for confirmation"
        recommendation = (
            "This setup passed Sentinel's market, trend, entry and risk rules. "
            "Review the chart, confirm the planned trigger, and use the calculated "
            "position size. Do not chase a price that has already moved beyond the "
            "planned entry area."
        )
    elif decision == "WATCH":
        headline = "Promising setup — confirmation is still missing"
        recommendation = (
            "Keep this stock on the watchlist. Do not enter yet. Wait until the "
            "weakest condition improves, then run Sentinel again before considering "
            "a position."
        )
    else:
        headline = "Low-quality setup — preserve capital"
        recommendation = (
            "Skip this setup today. A WAIT decision is useful because it protects "
            "capital for a clearer opportunity with stronger evidence and better risk."
        )

    if not risk_passes:
        risk_note = (
            "The trade plan failed Sentinel's risk rules. Do not override the stop, "
            "reward-to-risk, or position-size limits simply to make the trade fit."
        )
    elif reward_risk < MIN_REWARD_RISK:
        risk_note = (
            f"Reward-to-risk is only {reward_risk:.2f}R, below the "
            f"{MIN_REWARD_RISK:.1f}R minimum. Wait for a better entry or clearer target."
        )
    elif stop_percent <= 0:
        risk_note = "The stop distance is invalid. Do not trade until the plan is recalculated."
    else:
        risk_note = (
            f"The current plan offers {reward_risk:.2f}R with a "
            f"{stop_percent:.2f}% stop distance. Follow the calculated position size "
            "rather than increasing exposure based on confidence alone."
        )

    if market_status == "UNHEALTHY":
        market_note = "The wider market does not support new long positions."
    elif market_status == "CAUTION":
        market_note = "The wider market requires extra selectivity and smaller ambition."
    elif market_status == "HEALTHY":
        market_note = "The wider market currently supports selective long setups."
    else:
        market_note = "Market permission is unclear; treat the setup conservatively."

    if trend == "STRONG BULLISH":
        setup_type = "Strong bullish trend setup"
    elif trend == "BULLISH":
        setup_type = "Bullish trend setup"
    elif trend == "MIXED":
        setup_type = "Developing mixed-trend setup"
    else:
        setup_type = "Bearish or unconfirmed setup"

    primary_blocker = _first(
        warnings,
        "No major blocker was identified; execution discipline remains essential.",
    )
    immediate_action = _first(
        next_actions,
        "Continue monitoring and rerun Sentinel after the next daily close.",
    )

    return {
        "Coach Headline": headline,
        "Coach Recommendation": recommendation,
        "Coach Risk Note": risk_note,
        "Coach Market Note": market_note,
        "Coach Setup Type": setup_type,
        "Coach Primary Blocker": primary_blocker,
        "Coach Immediate Action": immediate_action,
        "Coach Summary": (
            f"{decision} with {confidence} confidence ({score}/100). "
            f"{market_note} {immediate_action}"
        ),
    }
