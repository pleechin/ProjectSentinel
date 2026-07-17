from modules.backtester import download_history, run_backtest
from strategies import ema_crossover, ema_volume


symbol = "NVDA"

history = download_history(symbol)

strategies = {
    "EMA Crossover": ema_crossover,
    "EMA + Volume": ema_volume,
}

for strategy_name, strategy_module in strategies.items():
    result = run_backtest(
        history,
        strategy=strategy_module,
    )

    print("\n" + "=" * 60)
    print(f"{strategy_name.upper()} — {symbol}")
    print("=" * 60)

    labels = {
        "trades": "Trades",
        "wins": "Wins",
        "losses": "Losses",
        "win_rate": "Win Rate %",
        "total_return": "Total Return %",
        "average_return": "Average Return %",
        "largest_winner": "Largest Winner %",
        "largest_loser": "Largest Loser %",
        "average_winner": "Average Winner %",
        "average_loser": "Average Loser %",
        "average_holding_days": "Average Holding Days",
        "profit_factor": "Profit Factor",
        "expectancy": "Expectancy %",
    }

    for key, label in labels.items():
        print(f"{label:<24}: {result['summary'][key]}")