import pandas as pd
import yfinance as yf

from indicators.ema import add_ema


def download_history(symbol, period="5y"):
    """
    Download historical price data.
    """

    print(f"Downloading {symbol}...")

    data = yf.download(
        symbol,
        period=period,
        auto_adjust=True,
        progress=False,
    )

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values("Price")

    return data


def run_backtest(history: pd.DataFrame):
    """
    Simple EMA20 / EMA50 crossover backtest.
    """

    history = add_ema(history)

    in_position = False
    entry_price = 0.0
    entry_date = None

    trades = []

    for i in range(1, len(history)):

        prev = history.iloc[i - 1]
        curr = history.iloc[i]

        curr_date = history.index[i]

        # BUY
        if (
            not in_position
            and prev["EMA20"] <= prev["EMA50"]
            and curr["EMA20"] > curr["EMA50"]
        ):

            in_position = True
            entry_price = curr["Close"]
            entry_date = curr_date

        # SELL
        elif (
            in_position
            and prev["EMA20"] >= prev["EMA50"]
            and curr["EMA20"] < curr["EMA50"]
        ):

            exit_price = curr["Close"]
            exit_date = curr_date

            trade_return = (
                (exit_price - entry_price)
                / entry_price
            ) * 100

            holding_days = (exit_date - entry_date).days

            trades.append({
                "buy_date": entry_date.date(),
                "buy_price": round(entry_price, 2),
                "sell_date": exit_date.date(),
                "sell_price": round(exit_price, 2),
                "return_pct": round(trade_return, 2),
                "holding_days": holding_days,
            })

            in_position = False

    total_trades = len(trades)
    wins = sum(1 for t in trades if t["return_pct"] > 0)
    losses = total_trades - wins

    total_return = sum(t["return_pct"] for t in trades)

    average_return = (
        total_return / total_trades
        if total_trades else 0
    )

    win_rate = (
        wins / total_trades * 100
        if total_trades else 0
    )

    return {
        "summary": {
            "trades": total_trades,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "total_return": round(total_return, 2),
            "average_return": round(average_return, 2),
        },
        "trades": trades,
    }