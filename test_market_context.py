import pandas as pd

from modules.market_context import get_market_context


def fake_history(close: float, ema_direction: str = "above") -> pd.DataFrame:
    values = [close - 10 + (i * 0.2) for i in range(60)]
    frame = pd.DataFrame({"Close": values})
    frame["EMA50"] = frame["Close"].ewm(span=50, adjust=False).mean()
    if ema_direction == "below":
        frame.loc[frame.index[-1], "Close"] = float(frame.iloc[-1]["EMA50"]) - 1
    else:
        frame.loc[frame.index[-1], "Close"] = float(frame.iloc[-1]["EMA50"]) + 1
    return frame


def bullish_loader(symbol: str) -> pd.DataFrame:
    if symbol == "^VIX":
        return pd.DataFrame({"Close": [18.0], "EMA50": [18.0]})
    return fake_history(100.0)


def defensive_loader(symbol: str) -> pd.DataFrame:
    if symbol == "^VIX":
        return pd.DataFrame({"Close": [25.0], "EMA50": [25.0]})
    return fake_history(100.0, "below")


def main() -> None:
    bullish = get_market_context(bullish_loader)
    assert bullish["market_score"] == 100
    assert bullish["market_status"] == "BULLISH"
    assert bullish["market_confidence"] == "HIGH"
    assert bullish["Permission"] is True
    assert len(bullish["drivers"]) == 4
    assert bullish["details"]["TREND_ALIGNMENT"] == "ALIGNED"

    defensive = get_market_context(defensive_loader)
    assert defensive["market_score"] == 0
    assert defensive["market_status"] == "DEFENSIVE"
    assert defensive["Permission"] is False

    for context in (bullish, defensive):
        assert 0 <= context["market_score"] <= 100
        assert context["Status"] in {"BULLISH", "NEUTRAL", "DEFENSIVE"}
        for symbol in ("SPY", "QQQ", "IWM", "^VIX"):
            assert symbol in context["details"]

    print("Market context tests passed.")


if __name__ == "__main__":
    main()
