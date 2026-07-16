import pandas as pd


def add_atr(
    history: pd.DataFrame,
    period: int = 14,
) -> pd.DataFrame:
    """Add a Wilder-style ATR column."""

    result = history.copy()
    previous_close = result["Close"].shift(1)

    true_range = pd.concat(
        [
            result["High"] - result["Low"],
            (result["High"] - previous_close).abs(),
            (result["Low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    result[f"ATR{period}"] = true_range.ewm(
        alpha=1 / period,
        adjust=False,
    ).mean()

    return result