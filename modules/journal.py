from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd


DEFAULT_JOURNAL_PATH = Path("data/trade_journal.csv")

JOURNAL_COLUMNS = [
    "Scan Timestamp UTC",
    "Data Date",
    "Symbol",
    "Decision",
    "Total Score",
    "Confidence",
    "Trend",
    "Entry Score",
    "Volume Ratio",
    "Suggested Entry",
    "Recommended Stop",
    "Resistance",
    "Reward Risk",
    "Position Size",
    "Risk Passes",
    "Coach Summary",
    "Journal Status",
]


def _normalise_date(value) -> str:
    if value is None or pd.isna(value):
        return ""
    try:
        return pd.Timestamp(value).date().isoformat()
    except (TypeError, ValueError):
        return str(value)


def _safe_float(value, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default: int = 0) -> int:
    try:
        if pd.isna(value):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def build_journal_entries(
    results: pd.DataFrame,
    decisions: Iterable[str] = ("CANDIDATE", "WATCH"),
    scan_timestamp: datetime | None = None,
) -> pd.DataFrame:
    """Convert ranked scan results into planned-opportunity journal rows."""

    if results.empty:
        return pd.DataFrame(columns=JOURNAL_COLUMNS)

    allowed = {str(value).upper() for value in decisions}
    selected = results[
        results["Decision"].astype(str).str.upper().isin(allowed)
    ]

    if selected.empty:
        return pd.DataFrame(columns=JOURNAL_COLUMNS)

    timestamp = scan_timestamp or datetime.now(timezone.utc)
    timestamp_text = timestamp.astimezone(timezone.utc).replace(
        microsecond=0
    ).isoformat()

    rows = []
    for _, row in selected.iterrows():
        rows.append(
            {
                "Scan Timestamp UTC": timestamp_text,
                "Data Date": _normalise_date(row.get("Data Date")),
                "Symbol": str(row.get("Symbol", "")).upper(),
                "Decision": str(row.get("Decision", "")).upper(),
                "Total Score": _safe_int(row.get("Total Score")),
                "Confidence": str(row.get("Confidence", "UNKNOWN")),
                "Trend": str(row.get("Trend", "UNKNOWN")).upper(),
                "Entry Score": _safe_int(row.get("Entry Score")),
                "Volume Ratio": round(_safe_float(row.get("Volume Ratio")), 4),
                "Suggested Entry": round(
                    _safe_float(row.get("Suggested Entry")), 4
                ),
                "Recommended Stop": round(
                    _safe_float(row.get("Recommended Stop")), 4
                ),
                "Resistance": round(
                    _safe_float(row.get("Resistance")), 4
                ),
                "Reward Risk": round(
                    _safe_float(row.get("Reward Risk")), 4
                ),
                "Position Size": _safe_int(row.get("Position Size")),
                "Risk Passes": bool(row.get("Risk Passes", False)),
                "Coach Summary": str(row.get("Coach Summary", "")),
                "Journal Status": "PLANNED",
            }
        )

    return pd.DataFrame(rows, columns=JOURNAL_COLUMNS)


def read_journal(path: str | Path = DEFAULT_JOURNAL_PATH) -> pd.DataFrame:
    """Read the journal, returning an empty correctly shaped table if absent."""

    journal_path = Path(path)
    if not journal_path.exists():
        return pd.DataFrame(columns=JOURNAL_COLUMNS)

    journal = pd.read_csv(journal_path)
    for column in JOURNAL_COLUMNS:
        if column not in journal.columns:
            journal[column] = ""

    return journal[JOURNAL_COLUMNS]


def _deduplication_key(frame: pd.DataFrame) -> pd.Series:
    return (
        frame["Data Date"].astype(str)
        + "|"
        + frame["Symbol"].astype(str).str.upper()
        + "|"
        + frame["Decision"].astype(str).str.upper()
    )


def save_planned_opportunities(
    results: pd.DataFrame,
    path: str | Path = DEFAULT_JOURNAL_PATH,
    decisions: Iterable[str] = ("CANDIDATE", "WATCH"),
    scan_timestamp: datetime | None = None,
) -> dict:
    """Append new planned opportunities while preventing duplicate daily rows."""

    journal_path = Path(path)
    new_entries = build_journal_entries(
        results=results,
        decisions=decisions,
        scan_timestamp=scan_timestamp,
    )
    existing = read_journal(journal_path)

    if new_entries.empty:
        return {
            "path": str(journal_path),
            "eligible": 0,
            "added": 0,
            "duplicates_skipped": 0,
            "total_rows": int(len(existing)),
        }

    existing_keys = set(_deduplication_key(existing)) if not existing.empty else set()
    new_keys = _deduplication_key(new_entries)
    duplicate_mask = new_keys.isin(existing_keys) | new_keys.duplicated(
        keep="first"
    )
    additions = new_entries.loc[~duplicate_mask].copy()

    if not additions.empty:
        journal_path.parent.mkdir(parents=True, exist_ok=True)
        if existing.empty:
            combined = additions.reset_index(drop=True)
        else:
            combined = pd.concat([existing, additions], ignore_index=True)
        combined.to_csv(journal_path, index=False)
    else:
        combined = existing

    return {
        "path": str(journal_path),
        "eligible": int(len(new_entries)),
        "added": int(len(additions)),
        "duplicates_skipped": int(duplicate_mask.sum()),
        "total_rows": int(len(combined)),
    }


def summarize_journal(journal: pd.DataFrame) -> dict:
    """Return lightweight statistics for the planned-opportunity journal."""

    if journal.empty:
        return {
            "total_rows": 0,
            "candidate_rows": 0,
            "watch_rows": 0,
            "unique_symbols": 0,
            "average_score": 0.0,
            "average_reward_risk": 0.0,
            "latest_data_date": None,
        }

    decisions = journal["Decision"].astype(str).str.upper()
    scores = pd.to_numeric(journal["Total Score"], errors="coerce")
    reward_risk = pd.to_numeric(journal["Reward Risk"], errors="coerce")
    dates = pd.to_datetime(journal["Data Date"], errors="coerce")

    latest_date = dates.max()

    return {
        "total_rows": int(len(journal)),
        "candidate_rows": int((decisions == "CANDIDATE").sum()),
        "watch_rows": int((decisions == "WATCH").sum()),
        "unique_symbols": int(journal["Symbol"].astype(str).nunique()),
        "average_score": round(float(scores.mean()), 1) if scores.notna().any() else 0.0,
        "average_reward_risk": (
            round(float(reward_risk.mean()), 2)
            if reward_risk.notna().any()
            else 0.0
        ),
        "latest_data_date": (
            latest_date.date().isoformat() if pd.notna(latest_date) else None
        ),
    }
