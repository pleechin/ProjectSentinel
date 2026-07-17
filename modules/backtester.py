import pandas as pd
import yfinance as yf

from indicators.ema import add_ema
from modules.analytics import calculate_equity_analytics
from modules.equity import build_equity_curve
from modules.performance import calculate_performance
from strategies import ema_crossover


DEFAULT_STARTING_CAPITAL = 100000.0


def download_history(
    symbol: str,
    period: str = "5y",
) -> pd.DataFrame:
    """
    Download and normalize historical price data.
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
    starting_capital: float = DEFAULT_STARTING_CAPITAL,
) -> dict:
    """
    Run a completed-trade backtest and return:
        summary
        trades
        equity_curve
        analytics
    """

    if starting_capital <= 0:
        raise ValueError("starting_capital must be greater than zero")

    if history.empty:
        equity_curve = []

        return {
            "summary": calculate_performance([]),
            "trades": [],
            "equity_curve": equity_curve,
            "analytics": calculate_equity_analytics(
                equity_curve,
                starting_capital=starting_capital,
            ),
        }

    if hasattr(strategy, "prepare"):
        history = strategy.prepare(history)
    else:
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
                (exit_price - entry_price)
                / entry_price
            ) * 100

            holding_days = (
                exit_date - entry_date
            ).days

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

    summary = calculate_performance(trades)

    equity_curve = build_equity_curve(
        trades,
        starting_capital=starting_capital,
    )

    analytics = calculate_equity_analytics(
        equity_curve,
        starting_capital=starting_capital,
    )

    return {
        "summary": summary,
        "trades": trades,
        "equity_curve": equity_curve,
        "analytics": analytics,
    }
