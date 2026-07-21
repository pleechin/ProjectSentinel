from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from modules.journal import DEFAULT_JOURNAL_PATH, read_journal


DEFAULT_LEARNING_REPORT_PATH = Path("reports/learning_report.txt")


def _numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(dtype="float64")
    return pd.to_numeric(frame[column], errors="coerce")


def _mode_text(series: pd.Series) -> str | None:
    cleaned = series.dropna().astype(str).str.strip()
    cleaned = cleaned[cleaned != ""]
    if cleaned.empty:
        return None
    modes = cleaned.mode()
    return str(modes.iloc[0]) if not modes.empty else None


def analyse_journal(journal: pd.DataFrame) -> dict[str, Any]:
    """Analyse planned-opportunity history without claiming trade performance."""

    if journal.empty:
        return {
            "status": "NO_DATA",
            "total_entries": 0,
            "unique_symbols": 0,
            "candidate_entries": 0,
            "watch_entries": 0,
            "average_score": 0.0,
            "average_reward_risk": 0.0,
            "average_entry_score": 0.0,
            "risk_pass_rate": 0.0,
            "latest_data_date": None,
            "most_frequent_symbol": None,
            "highest_average_score_symbol": None,
            "highest_average_score": 0.0,
            "highest_average_rr_symbol": None,
            "highest_average_rr": 0.0,
            "most_common_trend": None,
            "decision_breakdown": {},
            "top_symbols": [],
            "recommendations": [
                "Run Project Sentinel on multiple market days to build useful history."
            ],
        }

    working = journal.copy()
    working["Symbol"] = working["Symbol"].astype(str).str.upper()
    working["Decision"] = working["Decision"].astype(str).str.upper()

    scores = _numeric(working, "Total Score")
    reward_risk = _numeric(working, "Reward Risk")
    entry_scores = _numeric(working, "Entry Score")

    if "Risk Passes" in working.columns:
        risk_text = working["Risk Passes"].astype(str).str.upper()
        risk_passes = risk_text.isin({"TRUE", "1", "YES"})
    else:
        risk_passes = pd.Series(False, index=working.index)

    dates = pd.to_datetime(working.get("Data Date"), errors="coerce")
    latest_date = dates.max() if not dates.empty else pd.NaT

    decision_counts = (
        working["Decision"].value_counts().sort_index().astype(int).to_dict()
    )

    symbol_stats = (
        working.assign(
            _score=scores,
            _rr=reward_risk,
        )
        .groupby("Symbol", dropna=False)
        .agg(
            appearances=("Symbol", "size"),
            average_score=("_score", "mean"),
            average_reward_risk=("_rr", "mean"),
        )
        .reset_index()
    )

    symbol_stats["average_score"] = symbol_stats["average_score"].fillna(0.0)
    symbol_stats["average_reward_risk"] = symbol_stats[
        "average_reward_risk"
    ].fillna(0.0)

    frequency_ranked = symbol_stats.sort_values(
        ["appearances", "average_score", "Symbol"],
        ascending=[False, False, True],
        kind="mergesort",
    )
    score_ranked = symbol_stats.sort_values(
        ["average_score", "appearances", "Symbol"],
        ascending=[False, False, True],
        kind="mergesort",
    )
    rr_ranked = symbol_stats.sort_values(
        ["average_reward_risk", "appearances", "Symbol"],
        ascending=[False, False, True],
        kind="mergesort",
    )

    top_symbols = []
    for _, row in frequency_ranked.head(5).iterrows():
        top_symbols.append(
            {
                "symbol": str(row["Symbol"]),
                "appearances": int(row["appearances"]),
                "average_score": round(float(row["average_score"]), 1),
                "average_reward_risk": round(
                    float(row["average_reward_risk"]), 2
                ),
            }
        )

    recommendations: list[str] = []
    average_score = float(scores.mean()) if scores.notna().any() else 0.0
    average_rr = (
        float(reward_risk.mean()) if reward_risk.notna().any() else 0.0
    )
    pass_rate = float(risk_passes.mean() * 100) if len(risk_passes) else 0.0

    if len(working) < 20:
        recommendations.append(
            "The journal is still small; treat current patterns as preliminary."
        )
    if average_score < 65:
        recommendations.append(
            "Many logged setups have modest scores; keep filtering for stronger alignment."
        )
    else:
        recommendations.append(
            "The journal is generally capturing moderate-to-strong planned setups."
        )
    if average_rr < 2.0:
        recommendations.append(
            "Average planned reward-to-risk is below 2.0R; tighten selection before entry."
        )
    else:
        recommendations.append(
            "Average planned reward-to-risk meets the 2.0R preference."
        )
    if pass_rate < 70:
        recommendations.append(
            "A meaningful share of plans fail risk rules; prioritize risk-qualified setups."
        )
    recommendations.append(
        "This report analyses planned opportunities only; add executed outcomes before judging profitability."
    )

    best_score_row = score_ranked.iloc[0]
    best_rr_row = rr_ranked.iloc[0]
    most_frequent_row = frequency_ranked.iloc[0]

    return {
        "status": "READY",
        "total_entries": int(len(working)),
        "unique_symbols": int(working["Symbol"].nunique()),
        "candidate_entries": int((working["Decision"] == "CANDIDATE").sum()),
        "watch_entries": int((working["Decision"] == "WATCH").sum()),
        "average_score": round(average_score, 1),
        "average_reward_risk": round(average_rr, 2),
        "average_entry_score": (
            round(float(entry_scores.mean()), 1)
            if entry_scores.notna().any()
            else 0.0
        ),
        "risk_pass_rate": round(pass_rate, 1),
        "latest_data_date": (
            latest_date.date().isoformat() if pd.notna(latest_date) else None
        ),
        "most_frequent_symbol": str(most_frequent_row["Symbol"]),
        "highest_average_score_symbol": str(best_score_row["Symbol"]),
        "highest_average_score": round(
            float(best_score_row["average_score"]), 1
        ),
        "highest_average_rr_symbol": str(best_rr_row["Symbol"]),
        "highest_average_rr": round(
            float(best_rr_row["average_reward_risk"]), 2
        ),
        "most_common_trend": _mode_text(working.get("Trend", pd.Series(dtype=str))),
        "decision_breakdown": decision_counts,
        "top_symbols": top_symbols,
        "recommendations": recommendations,
    }


def build_learning_report(analysis: dict[str, Any]) -> str:
    """Render learning analysis as a readable plain-text report."""

    lines = [
        "=" * 72,
        "PROJECT SENTINEL — LEARNING ENGINE",
        "=" * 72,
    ]

    if analysis.get("status") == "NO_DATA":
        lines.extend(
            [
                "",
                "No journal data is available yet.",
                "Run Project Sentinel on multiple market days to build history.",
                "",
                "Important: the learning engine analyses planned opportunities,",
                "not actual trading profit or loss.",
            ]
        )
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            "",
            "JOURNAL SUMMARY",
            "-" * 72,
            f"Entries reviewed        : {analysis['total_entries']}",
            f"Unique symbols          : {analysis['unique_symbols']}",
            f"Latest market-data date : {analysis['latest_data_date'] or 'Unknown'}",
            f"Average total score     : {analysis['average_score']:.1f}/100",
            f"Average entry score     : {analysis['average_entry_score']:.1f}/100",
            f"Average reward-to-risk  : {analysis['average_reward_risk']:.2f}R",
            f"Risk-rule pass rate     : {analysis['risk_pass_rate']:.1f}%",
            "",
            "DECISION BREAKDOWN",
            "-" * 72,
        ]
    )

    for decision, count in analysis["decision_breakdown"].items():
        lines.append(f"{decision:<20}: {count}")

    lines.extend(
        [
            "",
            "OBSERVED PATTERNS",
            "-" * 72,
            f"Most frequent symbol    : {analysis['most_frequent_symbol']}",
            (
                "Highest average score  : "
                f"{analysis['highest_average_score_symbol']} "
                f"({analysis['highest_average_score']:.1f}/100)"
            ),
            (
                "Highest average R:R    : "
                f"{analysis['highest_average_rr_symbol']} "
                f"({analysis['highest_average_rr']:.2f}R)"
            ),
            f"Most common trend       : {analysis['most_common_trend'] or 'Unknown'}",
            "",
            "MOST FREQUENT SYMBOLS",
            "-" * 72,
            f"{'Symbol':<10}{'Entries':>10}{'Avg Score':>14}{'Avg R:R':>12}",
        ]
    )

    for item in analysis["top_symbols"]:
        lines.append(
            f"{item['symbol']:<10}{item['appearances']:>10}"
            f"{item['average_score']:>14.1f}"
            f"{item['average_reward_risk']:>11.2f}R"
        )

    lines.extend(["", "LEARNING NOTES", "-" * 72])
    for recommendation in analysis["recommendations"]:
        lines.append(f"• {recommendation}")

    lines.extend(
        [
            "",
            "LIMITATION",
            "-" * 72,
            "This journal currently stores planned CANDIDATE and WATCH setups.",
            "It cannot calculate win rate, profit factor, or the best strategy",
            "until actual entries, exits, and outcomes are recorded.",
        ]
    )

    return "\n".join(lines) + "\n"


def generate_learning_report(
    journal_path: str | Path = DEFAULT_JOURNAL_PATH,
    report_path: str | Path = DEFAULT_LEARNING_REPORT_PATH,
) -> dict[str, Any]:
    """Read the journal, analyse it, and save the learning report."""

    journal = read_journal(journal_path)
    analysis = analyse_journal(journal)
    report_text = build_learning_report(analysis)

    output_path = Path(report_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_text, encoding="utf-8")

    return {
        "path": str(output_path),
        "analysis": analysis,
        "report": report_text,
    }
