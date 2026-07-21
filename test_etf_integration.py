import pandas as pd

from config import ETF_SYMBOLS, STOCK_SYMBOLS, WATCHLIST_SYMBOLS
from modules.dashboard import build_dashboard_snapshot, filter_dashboard_results
from modules.ranking import rank_opportunities, summarize_portfolio
from watchlists.tradable_assets import ASSET_UNIVERSE


def row(symbol, asset_type, score, decision="WATCH"):
    return {
        "Symbol": symbol, "Asset Type": asset_type, "Category": "Test",
        "Decision": decision, "Total Score": score, "Reward Risk": 2.0,
        "Volume Ratio": 1.3, "Confidence": "HIGH", "Trend": "BULLISH",
        "Entry Score": 80, "Suggested Entry": 100.0, "Recommended Stop": 95.0,
        "Resistance": 110.0, "Coach Headline": "Test", "Coach Recommendation": "Test",
    }


def main():
    assert "SPY" in ETF_SYMBOLS
    assert "SMH" in ETF_SYMBOLS
    assert "NVDA" in STOCK_SYMBOLS
    assert len(WATCHLIST_SYMBOLS) == len(ASSET_UNIVERSE)

    ranked = rank_opportunities([row("SMH", "ETF", 90, "CANDIDATE"), row("NVDA", "STOCK", 85)])
    summary = summarize_portfolio(ranked)
    assert summary["assets_scanned"] == 2
    assert summary["stocks_scanned"] == 1
    assert summary["etfs_scanned"] == 1

    only_etfs = filter_dashboard_results(ranked, asset_types=["ETF"])
    assert only_etfs["Symbol"].tolist() == ["SMH"]

    market = {"Status": "HEALTHY", "Score": 80, "Permission": True, "Results": []}
    journal = pd.DataFrame()
    snapshot = build_dashboard_snapshot(market, ranked, journal)
    assert snapshot["top_etf"]["symbol"] == "SMH"
    assert snapshot["top_stock"]["symbol"] == "NVDA"
    print("ETF integration tests passed.")


if __name__ == "__main__":
    main()
