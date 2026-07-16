import pandas as pd


def print_report(
    market: dict,
    results: pd.DataFrame,
):
    """
    Display the final Project Sentinel report.
    """

    print()
    print("=" * 70)
    print("PROJECT SENTINEL")
    print("=" * 70)

    print(f"Market Status : {market['Status']}")
    print(f"Market Score  : {market['Score']:.0f}/100")

    print("=" * 70)

    if results.empty:
        print("No stocks analysed.")
        return

    candidates = results[
        results["Decision"] == "CANDIDATE"
    ]

    watch = results[
        results["Decision"] == "WATCH"
    ]

    wait = results[
        results["Decision"] == "WAIT"
    ]

    print(f"CANDIDATE : {len(candidates)}")
    print(f"WATCH     : {len(watch)}")
    print(f"WAIT      : {len(wait)}")

    print("=" * 70)

    print("TOP OPPORTUNITIES")

    for index, row in results.head(5).iterrows():

        print()

        print(f"#{index+1} {row['Symbol']}")
        print("-" * 45)

        print(f"Decision        : {row['Decision']}")
        print(f"Health          : {row['Health']}")
        print(f"Total Score     : {row['Total Score']}/100")

        print(f"Trend           : {row['Trend']}")

        print(f"Entry Score     : {row['Entry Score']}/100")

        print(f"Reward Risk     : {row['Reward Risk']:.2f}R")

        print(f"Position Size   : {int(row['Position Size'])}")

        print(
            f"Suggested Entry : ${row['Suggested Entry']:.2f}"
        )

        print(
            f"Stop Loss       : ${row['Recommended Stop']:.2f}"
        )

    print("=" * 70)

    print("End of Report")