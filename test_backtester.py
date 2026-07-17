from modules.backtester import (
    download_history,
    run_backtest,
)

data = download_history("NVDA")

result = run_backtest(data)

print("=" * 60)
print("BACKTEST SUMMARY")
print("=" * 60)

for key, value in result["summary"].items():
    print(f"{key:15}: {value}")

print("\n" + "=" * 60)
print("TRADE JOURNAL")
print("=" * 60)

for trade in result["trades"]:
    print(
        f"{trade['buy_date']} "
        f"@ {trade['buy_price']:8.2f}"
        f" -> "
        f"{trade['sell_date']} "
        f"@ {trade['sell_price']:8.2f} "
        f"| {trade['return_pct']:7.2f}% "
        f"| {trade['holding_days']:3} days"
    )