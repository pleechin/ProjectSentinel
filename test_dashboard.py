import pandas as pd

from modules.dashboard import (
    build_dashboard_snapshot,
    dashboard_table,
    filter_dashboard_results,
)


def sample_results() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Rank": 1,
                "Symbol": "AAA",
                "Decision": "CANDIDATE",
                "Total Score": 90,
                "Confidence": "HIGH",
                "Trend": "STRONG BULLISH",
                "Entry Score": 80,
                "Volume Ratio": 1.5,
                "Reward Risk": 2.5,
                "Suggested Entry": 100.0,
                "Recommended Stop": 95.0,
                "Resistance": 112.5,
                "Coach Headline": "Strong setup",
                "Coach Recommendation": "Review for entry.",
            },
            {
                "Rank": 2,
                "Symbol": "BBB",
                "Decision": "WATCH",
                "Total Score": 70,
                "Confidence": "MEDIUM",
                "Trend": "BULLISH",
                "Entry Score": 55,
                "Volume Ratio": 1.1,
                "Reward Risk": 1.8,
                "Suggested Entry": 50.0,
                "Recommended Stop": 47.0,
                "Resistance": 55.4,
                "Coach Headline": "Promising setup",
                "Coach Recommendation": "Wait for confirmation.",
            },
        ]
    )


def main() -> None:
    results = sample_results()
    market = {
        "Status": "HEALTHY",
        "Score": 87.5,
        "Permission": True,
        "Results": [],
    }
    journal = pd.DataFrame(
        [
            {
                "Data Date": "2026-07-20",
                "Symbol": "AAA",
                "Decision": "CANDIDATE",
                "Total Score": 90,
                "Reward Risk": 2.5,
                "Entry Score": 80,
                "Risk Passes": True,
                "Trend": "STRONG BULLISH",
            }
        ]
    )

    snapshot = build_dashboard_snapshot(market, results, journal)
    assert snapshot["market"]["status"] == "HEALTHY"
    assert snapshot["portfolio"]["candidates"] == 1
    assert snapshot["top_opportunity"]["symbol"] == "AAA"

    filtered = filter_dashboard_results(
        results,
        minimum_score=80,
        decisions=["CANDIDATE"],
    )
    assert filtered["Symbol"].tolist() == ["AAA"]

    compact = dashboard_table(results)
    assert "Coach Headline" in compact.columns
    assert len(compact) == 2

    print("Dashboard helper tests passed.")


if __name__ == "__main__":
    main()
