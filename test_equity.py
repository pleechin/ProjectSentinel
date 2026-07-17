from modules.backtester import (
    download_history,
    run_backtest,
)

from strategies import ema_volume

history = download_history("NVDA")

result = run_backtest(
    history,
    strategy=ema_volume,
)

print("\nEQUITY CURVE\n")

for row in result["equity_curve"]:

    print(
        f"{row['date']}   "
        f"Return {row['return_pct']:>7}%   "
        f"Capital RM{row['capital']:,.2f}"
    )