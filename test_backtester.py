from modules.backtester import download_history

data = download_history("NVDA")

print("=" * 60)
print("BACKTEST DATA")
print("=" * 60)

print(data.head())

print("\nRows downloaded :", len(data))
print("Columns          :", list(data.columns))
print("Index type       :", type(data.index).__name__)