import pandas as pd


def print_report(
    market: dict,
    results: pd.DataFrame,
) -> None:
    """Print a clear trading-coach report."""

    print()
    print("=" * 72)
    print("PROJECT SENTINEL — TRADING COACH")
    print("=" * 72)
    print(f"Market status : {market.get('Status', 'UNKNOWN')}")
    print(f"Market score  : {market.get('Score', 0):.0f}/100")
    print("=" * 72)

    if results.empty:
        print("No stocks were successfully analysed.")
        return

    candidate_count = int(
        (results["Decision"] == "CANDIDATE").sum()
    )
    watch_count = int(
        (results["Decision"] == "WATCH").sum()
    )
    wait_count = int(
        (results["Decision"] == "WAIT").sum()
    )

    print(f"Candidates : {candidate_count}")
    print(f"Watch      : {watch_count}")
    print(f"Wait       : {wait_count}")
    print()
    print("TOP FIVE OPPORTUNITIES")

    for position, (_, row) in enumerate(
        results.head(5).iterrows(),
        start=1,
    ):
        print()
        print("=" * 72)
        print(f"#{position} — {row['Symbol']}")
        print("-" * 50)

        print(f"Decision      : {row['Decision']}")
        print(f"Rating        : {row['Rating']}")
        print(f"Health        : {row['Health']}")
        print(f"Overall score : {row['Total Score']}/100")
        print(f"Trend         : {row['Trend']}")
        print(f"Entry score   : {row['Entry Score']}/100")

        print()
        print("TRADE PLAN")
        print(
            f"Suggested entry : "
            f"${row['Suggested Entry']:.2f}"
        )
        print(
            f"Recommended stop: "
            f"${row['Recommended Stop']:.2f}"
        )
        print(
            f"Resistance      : "
            f"${row['Resistance']:.2f}"
        )
        print(
            f"Reward-to-risk  : "
            f"{row['Reward Risk']:.2f}R"
        )
        print(
            f"Position size   : "
            f"{int(row['Position Size'])} shares"
        )
        print(
            f"Position value  : "
            f"RM{row['Position Value RM']:,.2f}"
        )
        print(
            f"Estimated loss  : "
            f"RM{row['Estimated Loss RM']:,.2f}"
        )
        print(
            f"Estimated profit: "
            f"RM{row['Estimated Profit RM']:,.2f}"
        )

        print()
        print("POSITIVE FACTORS")

        positive_factors = row["Positive Factors"]

        if positive_factors:
            for item in positive_factors:
                print(f"  ✓ {item}")
        else:
            print("  None identified.")

        print()
        print("WARNINGS")

        warnings = row["Warnings"]

        if warnings:
            for item in warnings:
                print(f"  • {item}")
        else:
            print("  No major warnings.")

        print()
        print("NEXT ACTION")

        next_actions = row["Next Action"]

        if next_actions:
            for item in next_actions:
                print(f"  → {item}")
        else:
            print("  → Continue monitoring.")

        print()
        print("TRADING COACH")
        print(f"  {row['Advice']}")

    print()
    print("=" * 72)
    print("End of report")
    print("CANDIDATE means review the chart; it is not an automatic order.")
    print("=" * 72)