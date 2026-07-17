from config import WATCHLIST_SYMBOLS
from modules.backtester import (
    download_history,
    run_backtest,
)

results = []

for symbol in WATCHLIST_SYMBOLS:

    print(f"\nTesting {symbol}...")

    data = download_history(symbol)

    result = run_backtest(data)

    results.append({
        "symbol": symbol,
        **result["summary"],
    })

print("\n" + "=" * 70)
print("PORTFOLIO SUMMARY")
print("=" * 70)

results.sort(
    key=lambda x: x["total_return"],
    reverse=True,
)

for r in results:

    print(
        f"{r['symbol']:6}"
        f"{r['trades']:>8}"
        f"{r['win_rate']:>10.2f}%"
        f"{r['total_return']:>12.2f}%"
    )