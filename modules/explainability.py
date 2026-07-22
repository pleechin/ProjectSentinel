"""Human-readable reasoning for Project Sentinel decisions."""

from __future__ import annotations


def build_explanation(score_result: dict, stock: dict) -> dict:
    components = [
        ("Market", score_result.get("Market Component", 0), 15),
        ("Sector", score_result.get("Sector Component", 0), 15),
        ("Industry", score_result.get("Industry Component", 0), 15),
        ("Trend", score_result.get("Trend Component", 0), 20),
        ("Momentum", score_result.get("Momentum Component", 0), 10),
        ("Volume", score_result.get("Volume Component", 0), 10),
        ("Risk", score_result.get("Risk Component", 0), 15),
    ]
    breakdown = [
        {"Component": name, "Score": int(value), "Maximum": maximum}
        for name, value, maximum in components
    ]
    strongest = max(components, key=lambda item: item[1] / item[2])
    weakest = min(components, key=lambda item: item[1] / item[2])
    why = list(score_result.get("Positive Factors", []))[:6]
    why_not = list(score_result.get("Warnings", []))[:5]
    return {
        "Why This Setup": why,
        "Why Not Higher": why_not,
        "Score Breakdown": breakdown,
        "Strongest Component": strongest[0],
        "Weakest Component": weakest[0],
        "Context Summary": (
            f"{stock.get('Sector Name') or 'Unmapped sector'} · "
            f"{stock.get('Industry Name') or 'Unmapped industry'}"
        ),
    }
