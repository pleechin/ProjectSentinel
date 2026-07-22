from __future__ import annotations

from modules.coach import build_coach_guidance
from modules.decision_card import build_decision_card
from modules.score import calculate_score


def evaluate_trade(
    market: dict,
    stock: dict,
    trade_plan: dict,
) -> dict:
    """Combine market, stock and risk information into one decision."""

    score_result = calculate_score(
        market=market,
        stock=stock,
        trade_plan=trade_plan,
    )

    market_status = str(market.get("Status", "UNKNOWN")).upper()
    market_permission = bool(market.get("Permission", False))
    trend = str(stock.get("Trend", "UNKNOWN")).upper()
    entry_score = int(stock.get("Entry Score", 0))
    risk_passes = bool(trade_plan.get("Risk Passes", False))
    total_score = int(score_result["Score"])

    candidate_passes = (
        market_permission
        and market_status == "HEALTHY"
        and trend in {"BULLISH", "STRONG BULLISH"}
        and entry_score >= 80
        and risk_passes
        and total_score >= 75
    )

    watch_passes = (
        market_permission
        and trend in {"BULLISH", "STRONG BULLISH", "MIXED"}
        and total_score >= 55
    )

    next_actions = list(score_result["Next Action"])

    if candidate_passes:
        decision = "CANDIDATE"
        next_actions.insert(
            0,
            "Review the chart and confirm the planned entry trigger",
        )
        advice = (
            "This is one of today's stronger setups. Review the chart carefully "
            "and wait for the planned entry trigger before taking any position."
        )
    elif watch_passes:
        decision = "WATCH"
        if not next_actions:
            next_actions.append("Continue monitoring for stronger confirmation")
        advice = (
            "Keep this stock on your watchlist. The setup has positive qualities, "
            "but it still needs better confirmation before entry."
        )
    else:
        decision = "WAIT"
        if not next_actions:
            next_actions.append("Do not open a new long position")
        advice = (
            "Skip this stock today. Capital is better preserved for a clearer "
            "and higher-quality opportunity."
        )

    next_actions = list(dict.fromkeys(next_actions))
    score_result_for_coach = {
        **score_result,
        "Next Action": next_actions,
    }
    decision_card = build_decision_card(
        decision=decision,
        score_result=score_result_for_coach,
        stock=stock,
        trade_plan=trade_plan,
        market=market,
    )

    coach = build_coach_guidance(
        market=market,
        stock=stock,
        trade_plan=trade_plan,
        score_result=score_result_for_coach,
        decision=decision,
    )

    return {
        "Decision": decision,
        "Confidence": score_result["Confidence"],
        "Confidence Score": total_score,
        "Health": score_result["Health"],
        "Rating": score_result["Rating"],
        "Advice": advice,
        "Total Score": total_score,
        "Market Component": score_result["Market Component"],
        "Trend Component": score_result["Trend Component"],
        "Entry Component": score_result["Entry Component"],
        "Risk Component": score_result["Risk Component"],
        "Sector Component": score_result.get("Sector Component", 0),
        "Industry Component": score_result.get("Industry Component", 0),
        "Momentum Component": score_result.get("Momentum Component", 0),
        "Volume Component": score_result.get("Volume Component", 0),
        "Positive Factors": score_result["Positive Factors"],
        "Warnings": score_result["Warnings"],
        "Next Action": next_actions,
        **decision_card,
        **coach,
    }
