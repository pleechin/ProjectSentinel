import pandas as pd
import yfinance as yf

# ============================================================
# Backtest settings
# ============================================================

SYMBOL = "AAPL"
HISTORY_PERIOD = "5y"

EMA20_PERIOD = 20
EMA50_PERIOD = 50
VOLUME_PERIOD = 20
ATR_PERIOD = 14

SUPPORT_LOOKBACK = 10
STOP_BUFFER_PERCENT = 0.5
ATR_MULTIPLIER = 2.0

MIN_VOLUME_RATIO = 1.20
MAX_HOLDING_DAYS = 10
TARGET_R_MULTIPLE = 2.0


def prepare_data(symbol: str) -> pd.DataFrame:
    """Download historical data and calculate indicators."""

    history = yf.Ticker(symbol).history(
        period=HISTORY_PERIOD,
        interval="1d",
    )

    history = history.dropna(
        subset=["Open", "High", "Low", "Close", "Volume"]
    ).copy()

    history["EMA20"] = history["Close"].ewm(
        span=EMA20_PERIOD,
        adjust=False,
    ).mean()

    history["EMA50"] = history["Close"].ewm(
        span=EMA50_PERIOD,
        adjust=False,
    ).mean()

    history["AverageVolume20"] = history["Volume"].rolling(
        window=VOLUME_PERIOD,
    ).mean()

    previous_close = history["Close"].shift(1)

    true_range = pd.concat(
        [
            history["High"] - history["Low"],
            (history["High"] - previous_close).abs(),
            (history["Low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    history["ATR14"] = true_range.ewm(
        alpha=1 / ATR_PERIOD,
        adjust=False,
    ).mean()

    return history.dropna().copy()


def backtest(symbol: str) -> pd.DataFrame:
    """
    Backtest the basic Sentinel pullback setup.

    Signal is calculated after a day's close.
    Entry occurs at the next trading day's open.
    """

    history = prepare_data(symbol)
    trades = []

    start_index = max(
        EMA50_PERIOD,
        SUPPORT_LOOKBACK,
        VOLUME_PERIOD,
    )

    index = start_index

    while index < len(history) - MAX_HOLDING_DAYS - 1:
        signal_day = history.iloc[index]

        close_price = float(signal_day["Close"])
        open_price = float(signal_day["Open"])
        ema20 = float(signal_day["EMA20"])
        ema50 = float(signal_day["EMA50"])
        volume = float(signal_day["Volume"])
        average_volume = float(signal_day["AverageVolume20"])
        atr14 = float(signal_day["ATR14"])

        distance_from_ema20 = (
            (close_price - ema20) / ema20
        ) * 100

        volume_ratio = (
            volume / average_volume
            if average_volume > 0
            else 0
        )

        bullish_trend = close_price > ema20 > ema50
        price_near_ema20 = -1.0 <= distance_from_ema20 <= 2.0
        bullish_candle = close_price > open_price
        strong_volume = volume_ratio >= MIN_VOLUME_RATIO

        signal_passes = (
            bullish_trend
            and price_near_ema20
            and bullish_candle
            and strong_volume
        )

        if not signal_passes:
            index += 1
            continue

        # Enter at the next trading day's open.
        entry_index = index + 1
        entry_day = history.iloc[entry_index]
        entry_price = float(entry_day["Open"])

        # Stop levels use only information available on signal day.
        previous_data = history.iloc[
            index - SUPPORT_LOOKBACK + 1:index + 1
        ]

        recent_support = float(
            previous_data["Low"].min()
        )

        swing_stop = recent_support * (
            1 - STOP_BUFFER_PERCENT / 100
        )

        atr_stop = entry_price - (
            ATR_MULTIPLIER * atr14
        )

        # Wider stop: below both support and normal volatility.
        stop_price = min(swing_stop, atr_stop)

        risk_per_share = entry_price - stop_price

        if risk_per_share <= 0:
            index += 1
            continue

        target_price = entry_price + (
            TARGET_R_MULTIPLE * risk_per_share
        )

        exit_price = None
        exit_date = None
        exit_reason = None
        holding_days = 0

        final_exit_index = min(
            entry_index + MAX_HOLDING_DAYS,
            len(history) - 1,
        )

        for future_index in range(
            entry_index,
            final_exit_index + 1,
        ):
            future_day = history.iloc[future_index]

            day_low = float(future_day["Low"])
            day_high = float(future_day["High"])
            day_close = float(future_day["Close"])

            holding_days = future_index - entry_index + 1

            # Conservative assumption:
            # if stop and target are both touched on one day,
            # count the stop as occurring first.
            if day_low <= stop_price:
                exit_price = stop_price
                exit_date = history.index[future_index]
                exit_reason = "STOP"
                break

            if day_high >= target_price:
                exit_price = target_price
                exit_date = history.index[future_index]
                exit_reason = "TARGET"
                break

            if future_index == final_exit_index:
                exit_price = day_close
                exit_date = history.index[future_index]
                exit_reason = "TIME EXIT"
                break

        profit_per_share = exit_price - entry_price
        result_r = profit_per_share / risk_per_share

        trades.append(
            {
                "Signal Date": history.index[index].date(),
                "Entry Date": history.index[entry_index].date(),
                "Exit Date": exit_date.date(),
                "Entry": entry_price,
                "Stop": stop_price,
                "Target": target_price,
                "Exit": exit_price,
                "Risk Per Share": risk_per_share,
                "Profit Per Share": profit_per_share,
                "Result R": result_r,
                "Holding Days": holding_days,
                "Exit Reason": exit_reason,
            }
        )

        # Avoid entering overlapping trades.
        index = future_index + 1

    return pd.DataFrame(trades)


def calculate_max_drawdown(results_r: pd.Series) -> float:
    """Calculate maximum drawdown from cumulative R results."""

    equity_curve = results_r.cumsum()
    running_high = equity_curve.cummax()
    drawdown = equity_curve - running_high

    return float(drawdown.min())


print("=" * 68)
print("Project Sentinel — Basic Historical Backtest")
print("=" * 68)
print(f"Stock             : {SYMBOL}")
print(f"History tested    : {HISTORY_PERIOD}")
print(f"Target            : {TARGET_R_MULTIPLE:.1f}R")
print(f"Maximum hold      : {MAX_HOLDING_DAYS} trading days")
print("=" * 68)

trades = backtest(SYMBOL)

if trades.empty:
    print("No historical trades matched the strategy.")
    raise SystemExit(0)

total_trades = len(trades)
winning_trades = trades[trades["Result R"] > 0]
losing_trades = trades[trades["Result R"] <= 0]

win_rate = (
    len(winning_trades) / total_trades
) * 100

average_r = float(trades["Result R"].mean())
total_r = float(trades["Result R"].sum())

gross_profit_r = float(
    winning_trades["Result R"].sum()
)

gross_loss_r = abs(
    float(losing_trades["Result R"].sum())
)

profit_factor = (
    gross_profit_r / gross_loss_r
    if gross_loss_r > 0
    else float("inf")
)

maximum_drawdown_r = calculate_max_drawdown(
    trades["Result R"]
)

average_holding_days = float(
    trades["Holding Days"].mean()
)

print("\nBACKTEST RESULTS")
print("-" * 45)
print(f"Total trades       : {total_trades}")
print(f"Winning trades     : {len(winning_trades)}")
print(f"Losing trades      : {len(losing_trades)}")
print(f"Win rate           : {win_rate:.2f}%")
print(f"Average result     : {average_r:.2f}R")
print(f"Total result       : {total_r:.2f}R")
print(f"Profit factor      : {profit_factor:.2f}")
print(f"Maximum drawdown   : {maximum_drawdown_r:.2f}R")
print(f"Average hold       : {average_holding_days:.1f} days")

print("\nLAST 10 HISTORICAL TRADES")
print("-" * 68)

columns_to_show = [
    "Signal Date",
    "Entry Date",
    "Exit Date",
    "Entry",
    "Stop",
    "Target",
    "Exit",
    "Result R",
    "Exit Reason",
]

print(
    trades[columns_to_show]
    .tail(10)
    .to_string(index=False)
)

print("\n" + "=" * 68)
print("This is an educational prototype, not proof of future profits.")
print("Fees, slippage, taxes and overnight gaps are not yet included.")
print("=" * 68)