import pandas as pd
import yfinance as yf

from indicators.ema import add_ema
from strategies import ema_crossover


def download_history(symbol: str, period: str = "5y") -> pd.DataFrame:
    """
    Download and normalize historical price data for one stock.
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


def run_backtest(
    history: pd.DataFrame,
    strategy=ema_crossover,
) -> dict:
    """
    Run a backtest using the supplied trading strategy.
    """

    if history.empty:
        return {
            "summary": {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "total_return": 0.0,
                "average_return": 0.0,
            },
            "trades": [],
        }

    history = add_ema(history)

    in_position = False
    entry_price = 0.0
    entry_date = None

    trades = []

    for i in range(1, len(history)):
        previous_row = history.iloc[i - 1]
        current_row = history.iloc[i]
        current_date = history.index[i]

        if (
            not in_position
            and strategy.buy_signal(previous_row, current_row)
        ):
            in_position = True
            entry_price = float(current_row["Close"])
            entry_date = current_date

        elif (
            in_position
            and strategy.sell_signal(previous_row, current_row)
        ):
            exit_price = float(current_row["Close"])
            exit_date = current_date

            trade_return = (
                (exit_price - entry_price) / entry_price
            ) * 100

            holding_days = (exit_date - entry_date).days

            trades.append(
                {
                    "buy_date": entry_date.date(),
                    "buy_price": round(entry_price, 2),
                    "sell_date": exit_date.date(),
                    "sell_price": round(exit_price, 2),
                    "return_pct": round(trade_return, 2),
                    "holding_days": holding_days,
                }
            )

            in_position = False
            entry_price = 0.0
            entry_date = None

    total_trades = len(trades)
    wins = sum(
        1 for trade in trades
        if trade["return_pct"] > 0
    )
    losses = total_trades - wins

    total_return = sum(
        trade["return_pct"]
        for trade in trades
    )

    win_rate = (
        wins / total_trades * 100
        if total_trades
        else 0.0
    )

    average_return = (
        total_return / total_trades
        if total_trades
        else 0.0
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