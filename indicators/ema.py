import pandas as pd


def add_ema(
    history: pd.DataFrame,
    periods: tuple[int, ...] = (20, 50, 200),
) -> pd.DataFrame:
    """Add EMA columns such as EMA20, EMA50 and EMA200."""

    result = history.copy()

    for period in periods:
        result[f"EMA{period}"] = result["Close"].ewm(
            span=period,
            adjust=False,
        ).mean()

    return result