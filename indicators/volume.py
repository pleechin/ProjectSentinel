import pandas as pd


def add_average_volume(
    history: pd.DataFrame,
    period: int = 20,
) -> pd.DataFrame:
    """Add Average Volume column."""

    result = history.copy()

    result[f"AvgVolume{period}"] = (
        result["Volume"]
        .rolling(window=period)
        .mean()
    )

    return result