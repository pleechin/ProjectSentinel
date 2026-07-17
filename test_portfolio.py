from modules.portfolio import run_portfolio_backtest

results = run_portfolio_backtest()

print("\n" + "=" * 70)
print("PORTFOLIO BACKTEST")
print("=" * 70)

print(
    f"{'Symbol':<8}"
    f"{'Trades':>8}"
    f"{'Win %':>10}"
    f"{'Return %':>12}"
)

print("-" * 70)

for r in results:

    print(
        f"{r['symbol']:<8}"
        f"{r['trades']:>8}"
        f"{r['win_rate']:>9.2f}%"
        f"{r['total_return']:>11.2f}%"
    )