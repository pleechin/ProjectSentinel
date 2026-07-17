from modules.backtester import download_history

data = download_history("NVDA")

print("=" * 60)
print("BACKTEST DATA")
print("=" * 60)

print(data.head())

print()

print(f"Rows downloaded : {len(data)}")