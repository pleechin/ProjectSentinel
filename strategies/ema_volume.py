import pandas as pd

from indicators.ema import add_ema
from indicators.volume import add_average_volume


def prepare(history: pd.DataFrame) -> pd.DataFrame:
    """
    Add the indicators required by the EMA-volume strategy.
    """

    result = add_ema(history)
    result = add_average_volume(result, period=20)

    return result


def buy_signal(
    previous_row: pd.Series,
    current_row: pd.Series,
) -> bool:
    """
    Buy when EMA20 crosses above EMA50 and current volume
    is above its 20-day average.
    """

    ema_crossed_up = (
        previous_row["EMA20"] <= previous_row["EMA50"]
        and current_row["EMA20"] > current_row["EMA50"]
    )

    volume_confirmed = (
        pd.notna(current_row["AvgVolume20"])
        and current_row["Volume"] > current_row["AvgVolume20"]
    )

    return bool(ema_crossed_up and volume_confirmed)


def sell_signal(
    previous_row: pd.Series,
    current_row: pd.Series,
) -> bool:
    """
    Sell when EMA20 crosses below EMA50.
    """

    ema_crossed_down = (
        previous_row["EMA20"] >= previous_row["EMA50"]
        and current_row["EMA20"] < current_row["EMA50"]
    )

    return bool(ema_crossed_down)