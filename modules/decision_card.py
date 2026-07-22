from __future__ import annotations

from typing import Any

from modules.decision_intelligence import build_decision_intelligence


def _unique_text(items: list[Any] | tuple[Any, ...] | None) -> list[str]:
    output: list[str] = []
    for item in items or []:
        text = str(item).strip()
        if text and text not in output:
            output.append(text)
    return output


def build_decision_card(
    decision: str,
    score_result: dict[str, Any],
    stock: dict[str, Any],
    trade_plan: dict[str, Any],
    market: dict[str, Any],
) -> dict[str, Any]:
    """Build a balanced decision card with bull case, bear case and action."""
    why_buy = _unique_text(score_result.get("Positive Factors", []))
    why_not_buy = _unique_text(score_result.get("Warnings", []))
    what_to_watch = _unique_text(score_result.get("Next Action", []))

    market_status = str(market.get("Status", market.get("market_status", "UNKNOWN"))).upper()
    trend = str(stock.get("Trend", "UNKNOWN")).upper()
    entry = float(trade_plan.get("Suggested Entry", 0.0) or 0.0)
    stop = float(trade_plan.get("Recommended Stop", 0.0) or 0.0)
    resistance = float(trade_plan.get("Resistance", 0.0) or 0.0)
    reward_risk = float(trade_plan.get("Reward Risk", 0.0) or 0.0)
    position_size = int(trade_plan.get("Position Size", 0) or 0)

    if not why_buy:
        why_buy = ["No strong positive confirmation is present yet"]
    if not why_not_buy:
        why_not_buy = ["No major technical or risk blocker was detected"]
    if not what_to_watch:
        what_to_watch = ["Rerun Sentinel after the next daily close"]

    invalidation: list[str] = []
    if stop > 0:
        invalidation.append(f"Price closes below the planned stop near ${stop:.2f}")
    if market_status in {"HEALTHY", "BULLISH"}:
        invalidation.append("The wider market loses long-trade permission")
    if trend in {"BULLISH", "STRONG BULLISH"}:
        invalidation.append("The bullish EMA trend breaks down")
    invalidation = _unique_text(invalidation) or ["The current setup conditions materially weaken"]

    if decision == "CANDIDATE":
        action = "Wait for the planned entry trigger, confirm the chart, then use the calculated position size."
    elif decision == "WATCH":
        action = "Keep this asset on the watchlist and wait for the missing confirmations before entry."
    else:
        action = "Do not open a new position now. Preserve capital until the setup improves."

    intelligence = build_decision_intelligence(
        decision=decision,
        score_result=score_result,
        stock=stock,
        trade_plan=trade_plan,
        market=market,
    )

    return {
        "Why Buy": why_buy,
        "Why Not Buy": why_not_buy,
        "What To Watch": what_to_watch,
        "Invalidation": invalidation,
        "Recommended Action": action,
        "Trade Plan": {
            "Entry": entry,
            "Stop": stop,
            "Resistance": resistance,
            "Reward Risk": reward_risk,
            "Position Size": position_size,
        },
        **intelligence,
    }
