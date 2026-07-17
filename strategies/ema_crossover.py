def buy_signal(prev, curr):
    """
    EMA20 crosses above EMA50.
    """

    return (
        prev["EMA20"] <= prev["EMA50"]
        and curr["EMA20"] > curr["EMA50"]
    )


def sell_signal(prev, curr):
    """
    EMA20 crosses below EMA50.
    """

    return (
        prev["EMA20"] >= prev["EMA50"]
        and curr["EMA20"] < curr["EMA50"]
    )