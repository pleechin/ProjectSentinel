from __future__ import annotations

from typing import Iterable
import pandas as pd

DECISION_PRIORITY = {"CANDIDATE": 3, "WATCH": 2, "WAIT": 1}


def rank_opportunities(results: Iterable[dict] | pd.DataFrame) -> pd.DataFrame:
    """Return Sentinel opportunities in a deterministic best-first order."""
    ranking = results.copy() if isinstance(results, pd.DataFrame) else pd.DataFrame(list(results))
    if ranking.empty:
        return ranking

    required = {"Symbol", "Decision", "Total Score", "Reward Risk", "Volume Ratio"}
    missing = sorted(required.difference(ranking.columns))
    if missing:
        raise ValueError("Ranking data is missing required columns: " + ", ".join(missing))

    if "Asset Type" not in ranking.columns:
        ranking["Asset Type"] = "STOCK"
    if "Category" not in ranking.columns:
        ranking["Category"] = "Unclassified"

    ranking["Decision Rank"] = (
        ranking["Decision"].astype(str).str.upper().map(DECISION_PRIORITY).fillna(0).astype(int)
    )
    ranking = ranking.sort_values(
        by=["Decision Rank", "Total Score", "Reward Risk", "Volume Ratio", "Symbol"],
        ascending=[False, False, False, False, True],
        kind="mergesort",
    ).reset_index(drop=True)
    ranking.insert(0, "Rank", range(1, len(ranking) + 1))
    return ranking


def summarize_portfolio(ranking: pd.DataFrame) -> dict:
    """Build scan-level statistics for stocks and ETFs."""
    if ranking.empty:
        return {
            "assets_scanned": 0, "stocks_scanned": 0, "etfs_scanned": 0,
            "candidates": 0, "watch": 0, "wait": 0, "average_score": 0.0,
            "highest_symbol": None, "highest_score": 0,
            "lowest_symbol": None, "lowest_score": 0,
        }

    decisions = ranking["Decision"].astype(str).str.upper()
    asset_types = ranking.get("Asset Type", pd.Series("STOCK", index=ranking.index)).astype(str).str.upper()
    highest = ranking.loc[ranking["Total Score"].idxmax()]
    lowest = ranking.loc[ranking["Total Score"].idxmin()]
    return {
        "assets_scanned": int(len(ranking)),
        "stocks_scanned": int((asset_types == "STOCK").sum()),
        "etfs_scanned": int((asset_types == "ETF").sum()),
        "candidates": int((decisions == "CANDIDATE").sum()),
        "watch": int((decisions == "WATCH").sum()),
        "wait": int((decisions == "WAIT").sum()),
        "average_score": round(float(ranking["Total Score"].mean()), 1),
        "highest_symbol": str(highest["Symbol"]),
        "highest_score": int(highest["Total Score"]),
        "lowest_symbol": str(lowest["Symbol"]),
        "lowest_score": int(lowest["Total Score"]),
    }


def filter_opportunities(ranking: pd.DataFrame, minimum_score: int = 0, decisions=None) -> pd.DataFrame:
    """Filter a ranked table without changing original ranks."""
    if ranking.empty:
        return ranking.copy()
    filtered = ranking[ranking["Total Score"] >= int(minimum_score)].copy()
    if decisions:
        allowed = {str(decision).upper() for decision in decisions}
        filtered = filtered[filtered["Decision"].astype(str).str.upper().isin(allowed)]
    return filtered.reset_index(drop=True)
