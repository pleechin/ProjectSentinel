from __future__ import annotations

from typing import Any


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item.strip() for item in items if str(item).strip()))


def confidence_label(score: int) -> str:
    if score >= 90:
        return "HIGH CONVICTION"
    if score >= 75:
        return "GOOD SETUP"
    if score >= 60:
        return "NEEDS CONFIRMATION"
    if score >= 45:
        return "WEAK SETUP"
    return "AVOID FOR NOW"


def build_decision_intelligence(
    decision: str,
    score_result: dict[str, Any],
    stock: dict[str, Any],
    trade_plan: dict[str, Any],
    market: dict[str, Any],
) -> dict[str, Any]:
    """Challenge a setup, explain confidence, and create coach guidance."""
    score = int(score_result.get("Score", 0) or 0)
    warnings = [str(item) for item in score_result.get("Warnings", [])]
    positives = [str(item) for item in score_result.get("Positive Factors", [])]

    market_score = float(market.get("Score", market.get("market_score", 0)) or 0)
    market_permission = bool(market.get("Permission", market.get("permission", False)))
    sector_score = float(stock.get("Sector Score", 50) or 50)
    industry_score = float(stock.get("Industry Score", 50) or 50)
    trend = str(stock.get("Trend", "UNKNOWN")).upper()
    volume_ratio = float(stock.get("Volume Ratio", 0) or 0)
    ema_distance = float(stock.get("EMA20 Distance %", 0) or 0)
    reward_risk = float(trade_plan.get("Reward Risk", 0) or 0)
    stop_distance = float(trade_plan.get("Stop Distance %", 0) or 0)
    risk_passes = bool(trade_plan.get("Risk Passes", False))

    reject_reasons: list[str] = []
    if not market_permission or market_score < 55:
        reject_reasons.append("The broad market does not provide strong long-trade support")
    if sector_score < 50:
        reject_reasons.append("The mapped sector is not showing leadership")
    if industry_score < 50:
        reject_reasons.append("The mapped industry is not showing leadership")
    if trend not in {"BULLISH", "STRONG BULLISH"}:
        reject_reasons.append("The stock trend is not fully bullish")
    if volume_ratio < 1.0:
        reject_reasons.append("Buying volume is below its 20-day average")
    if ema_distance > 5:
        reject_reasons.append("Price is extended more than 5% above EMA20")
    if reward_risk < 2.0:
        reject_reasons.append("The reward-to-risk ratio is below 2R")
    if not risk_passes:
        reject_reasons.append("The current trade plan does not pass Sentinel risk rules")
    if stop_distance <= 0:
        reject_reasons.append("A valid stop distance has not been established")

    reject_reasons = _unique(reject_reasons + warnings)
    strengths = _unique(positives)

    severe_count = sum([
        not market_permission,
        trend not in {"BULLISH", "STRONG BULLISH"},
        reward_risk < 1.5,
        not risk_passes,
    ])

    if decision == "CANDIDATE" and severe_count == 0 and len(reject_reasons) <= 3:
        verdict = "The bull case is stronger, but the remaining risks must still be respected."
        coach = "Use the planned entry and position size. Do not chase above the trigger, and cancel the setup if an invalidation condition appears."
    elif decision in {"CANDIDATE", "WATCH"}:
        verdict = "The setup has useful strengths, but confirmation is not yet strong enough for an unrestricted entry."
        coach = "Keep it on the watchlist. Enter only after the listed blockers improve and the risk plan passes again."
    else:
        verdict = "The bear case currently outweighs the available bullish evidence."
        coach = "Preserve capital. Review the asset again after the market, trend, volume, or reward-to-risk improves."

    confidence_explanation = (
        f"{score}/100 reflects {len(strengths)} supporting factor(s) and "
        f"{len(reject_reasons)} risk or confirmation issue(s)."
    )

    return {
        "Confidence Label": confidence_label(score),
        "Confidence Explanation": confidence_explanation,
        "Bull Case": strengths or ["No strong bullish evidence is confirmed yet"],
        "Bear Case": reject_reasons or ["No major rejection reason was detected"],
        "Devils Advocate Verdict": verdict,
        "Coach Advice": coach,
        "Risk Count": len(reject_reasons),
    }
