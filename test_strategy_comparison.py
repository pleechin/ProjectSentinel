from modules.backtester import download_history, run_backtest
from strategies import ema_crossover, ema_volume


symbol = "NVDA"
history = download_history(symbol)

strategies = {
    "EMA Crossover": ema_crossover,
    "EMA + Volume": ema_volume,
}

print("=" * 78)
print(f"STRATEGY COMPARISON — {symbol}")
print("=" * 78)

print(
    f"{'Strategy':<22}"
    f"{'Trades':>8}"
    f"{'Win %':>10}"
    f"{'Return %':>12}"
    f"{'Avg Return %':>15}"
)

print("-" * 78)

for strategy_name, strategy_module in strategies.items():
    result = run_backtest(
        history,
        strategy=strategy_module,
    )

    summary = result["summary"]

    print(
        f"{strategy_name:<22}"
        f"{summary['trades']:>8}"
        f"{summary['win_rate']:>10.2f}"
        f"{summary['total_return']:>12.2f}"
        f"{summary['average_return']:>15.2f}"
    )