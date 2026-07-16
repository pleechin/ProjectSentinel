import pandas as pd


def add_average_volume(
    history: pd.DataFrame,
    period: int = 20,
) -> pd.DataFrame:
    """Add an average-volume column."""

    result = history.copy()

    result[f"AverageVolume{period}"] = result["Volume"].rolling(
        window=period,
    ).mean()

    return result