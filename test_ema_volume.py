from modules.backtester import download_history, run_backtest
from strategies import ema_volume

history = download_history("NVDA")

result = run_backtest(
    history,
    strategy=ema_volume,
)

print("=" * 60)
print("EMA + VOLUME BACKTEST")
print("=" * 60)

for key, value in result["summary"].items():
    print(f"{key:15}: {value}")