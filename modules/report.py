from __future__ import annotations

import pandas as pd

from modules.ranking import summarize_portfolio


def _format_money(value: float) -> str:
    return f"RM{float(value):,.2f}"


def _print_ranking_table(results: pd.DataFrame) -> None:
    print("RANKED OPPORTUNITIES")
    print("-" * 88)
    print(
        f"{'Rank':>4}  {'Symbol':<7} {'Score':>5}  "
        f"{'Confidence':<10} {'Decision':<10} {'Trend':<15} {'R:R':>6}"
    )
    print("-" * 88)

    for _, row in results.iterrows():
        print(
            f"{int(row['Rank']):>4}  {row['Symbol']:<7} "
            f"{int(row['Total Score']):>5}  {row['Confidence']:<10} "
            f"{row['Decision']:<10} {row['Trend']:<15} "
            f"{float(row['Reward Risk']):>5.2f}R"
        )


def _print_items(items, prefix: str, empty_message: str) -> None:
    values = list(items) if isinstance(items, (list, tuple)) else []
    if values:
        for item in values:
            print(f"  {prefix} {item}")
    else:
        print(f"  {empty_message}")


def print_report(
    market: dict,
    results: pd.DataFrame,
    top_n: int = 5,
) -> None:
    """Print ranked opportunities and deterministic coach guidance."""

    print()
    print("=" * 88)
    print("PROJECT SENTINEL — PORTFOLIO RANKING & TRADING COACH")
    print("=" * 88)
    print(f"Market status : {market.get('Status', 'UNKNOWN')}")
    print(f"Market score  : {float(market.get('Score', 0)):.0f}/100")
    print("=" * 88)

    if results.empty:
        print("No stocks were successfully analysed.")
        return

    summary = summarize_portfolio(results)
    print("PORTFOLIO SUMMARY")
    print(f"Stocks scanned : {summary['stocks_scanned']}")
    print(f"Candidates     : {summary['candidates']}")
    print(f"Watch          : {summary['watch']}")
    print(f"Wait           : {summary['wait']}")
    print(f"Average score  : {summary['average_score']:.1f}/100")
    print(
        f"Highest score  : {summary['highest_symbol']} "
        f"({summary['highest_score']}/100)"
    )
    print(
        f"Lowest score   : {summary['lowest_symbol']} "
        f"({summary['lowest_score']}/100)"
    )
    print()

    _print_ranking_table(results)

    detail_count = min(max(int(top_n), 0), len(results))
    print()
    print(f"TOP {detail_count} COACH REVIEWS")

    for _, row in results.head(detail_count).iterrows():
        print()
        print("=" * 88)
        print(f"#{int(row['Rank'])} — {row['Symbol']}")
        print("-" * 88)
        print(f"Decision         : {row['Decision']}")
        print(
            f"Confidence       : {row['Confidence']} "
            f"({int(row['Confidence Score'])}/100)"
        )
        print(f"Coach headline   : {row['Coach Headline']}")
        print(f"Setup type       : {row['Coach Setup Type']}")
        print(f"Rating           : {row['Rating']}")
        print(f"Health           : {row['Health']}")
        print(f"Trend            : {row['Trend']}")
        print(f"Entry score      : {int(row['Entry Score'])}/100")

        print()
        print("SCORE BREAKDOWN")
        print(f"  Market : {int(row['Market Component'])}/20")
        print(f"  Trend  : {int(row['Trend Component'])}/30")
        print(f"  Entry  : {int(row['Entry Component'])}/30")
        print(f"  Risk   : {int(row['Risk Component'])}/20")

        print()
        print("TRADE PLAN")
        print(f"Suggested entry : ${float(row['Suggested Entry']):.2f}")
        print(f"Recommended stop: ${float(row['Recommended Stop']):.2f}")
        print(f"Resistance      : ${float(row['Resistance']):.2f}")
        print(f"Reward-to-risk  : {float(row['Reward Risk']):.2f}R")
        print(f"Position size   : {int(row['Position Size'])} shares")
        print(f"Position value  : {_format_money(row['Position Value RM'])}")
        print(f"Estimated loss  : {_format_money(row['Estimated Loss RM'])}")
        print(f"Estimated profit: {_format_money(row['Estimated Profit RM'])}")

        print()
        print("STRENGTHS")
        _print_items(row["Positive Factors"], "✓", "None identified.")

        print()
        print("RISKS / WEAKNESSES")
        _print_items(row["Warnings"], "•", "No major warnings.")

        print()
        print("COACH GUIDANCE")
        print(f"  Market view   : {row['Coach Market Note']}")
        print(f"  Main blocker  : {row['Coach Primary Blocker']}")
        print(f"  Immediate step: {row['Coach Immediate Action']}")
        print(f"  Risk note     : {row['Coach Risk Note']}")

        print()
        print("COACH RECOMMENDATION")
        print(f"  {row['Coach Recommendation']}")

    print()
    print("=" * 88)
    print("Sentinel is decision support, not an automatic trading instruction.")
    print("=" * 88)
