from __future__ import annotations
from typing import Any
import pandas as pd
from modules.journal import summarize_journal
from modules.learning import analyse_journal
from modules.ranking import summarize_portfolio


def build_dashboard_snapshot(
    market: dict[str, Any],
    results: pd.DataFrame,
    journal: pd.DataFrame,
    sectors: dict[str, Any] | None = None,
    industries: dict[str, Any] | None = None,
) -> dict[str, Any]:
    portfolio = summarize_portfolio(results)
    journal_summary = summarize_journal(journal)
    learning = analyse_journal(journal)

    def top_for(asset_type: str):
        if results.empty or "Asset Type" not in results.columns:
            return None
        subset = results[results["Asset Type"].astype(str).str.upper() == asset_type]
        if subset.empty:
            return None
        row = subset.iloc[0]
        return {
            "symbol": str(row.get("Symbol", "")), "decision": str(row.get("Decision", "UNKNOWN")),
            "score": int(row.get("Total Score", 0)), "confidence": str(row.get("Confidence", "UNKNOWN")),
            "reward_risk": float(row.get("Reward Risk", 0.0)), "category": str(row.get("Category", "")),
            "headline": str(row.get("Coach Headline", "")),
            "recommendation": str(row.get("Coach Recommendation", "")),
        }

    top_any = None if results.empty else {
        "symbol": str(results.iloc[0].get("Symbol", "")),
        "decision": str(results.iloc[0].get("Decision", "UNKNOWN")),
        "score": int(results.iloc[0].get("Total Score", 0)),
        "confidence": str(results.iloc[0].get("Confidence", "UNKNOWN")),
        "reward_risk": float(results.iloc[0].get("Reward Risk", 0.0)),
        "category": str(results.iloc[0].get("Category", "")),
        "asset_type": str(results.iloc[0].get("Asset Type", "ASSET")),
        "headline": str(results.iloc[0].get("Coach Headline", "")),
        "recommendation": str(results.iloc[0].get("Coach Recommendation", "")),
    }

    return {
        "market": {
            "status": str(market.get("Status", market.get("market_status", "UNKNOWN"))),
            "score": float(market.get("Score", market.get("market_score", 0.0))),
            "confidence": str(market.get("Confidence", market.get("market_confidence", "UNKNOWN"))),
            "permission": bool(market.get("Permission", False)),
            "indexes": list(market.get("Results", market.get("drivers", []))),
            "details": dict(market.get("details", {})),
        },
        "portfolio": portfolio, "journal": journal_summary, "learning": learning,
        "sectors": sectors or {"status": "NO_DATA", "rankings": [], "leaders": [], "laggards": []},
        "industries": industries or {"status": "NO_DATA", "rankings": [], "leaders": [], "laggards": []},
        "top_opportunity": top_any, "top_stock": top_for("STOCK"), "top_etf": top_for("ETF"),
    }


def dashboard_table(results: pd.DataFrame) -> pd.DataFrame:
    columns = ["Rank", "Asset Type", "Symbol", "Category", "Decision", "Total Score", "Confidence",
               "Trend", "Entry Score", "Volume Ratio", "Reward Risk", "Suggested Entry",
               "Recommended Stop", "Resistance", "Coach Headline"]
    if results.empty:
        return pd.DataFrame(columns=columns)
    return results[[column for column in columns if column in results.columns]].copy()


def filter_dashboard_results(results: pd.DataFrame, minimum_score: int = 0, decisions=None, asset_types=None) -> pd.DataFrame:
    if results.empty:
        return results.copy()
    filtered = results[pd.to_numeric(results["Total Score"], errors="coerce").fillna(0) >= int(minimum_score)].copy()
    if decisions:
        allowed = {str(value).upper() for value in decisions}
        filtered = filtered[filtered["Decision"].astype(str).str.upper().isin(allowed)]
    if asset_types and "Asset Type" in filtered.columns:
        allowed_types = {str(value).upper() for value in asset_types}
        filtered = filtered[filtered["Asset Type"].astype(str).str.upper().isin(allowed_types)]
    return filtered.reset_index(drop=True)
