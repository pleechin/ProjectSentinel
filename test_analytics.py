from modules.backtester import download_history, run_backtest
from strategies import ema_crossover, ema_volume


SYMBOL = "NVDA"
STARTING_CAPITAL = 100000.0

STRATEGIES = {
    "EMA Crossover": ema_crossover,
    "EMA + Volume": ema_volume,
}


history = download_history(SYMBOL)

for strategy_name, strategy_module in STRATEGIES.items():
    result = run_backtest(
        history,
        strategy=strategy_module,
        starting_capital=STARTING_CAPITAL,
    )

    summary = result["summary"]
    analytics = result["analytics"]

    print("\n" + "=" * 64)
    print(f"{strategy_name.upper()} — {SYMBOL}")
    print("=" * 64)

    print(
        f"{'Trades':<28}: "
        f"{summary['trades']}"
    )
    print(
        f"{'Win Rate':<28}: "
        f"{summary['win_rate']:.2f}%"
    )
    print(
        f"{'Profit Factor':<28}: "
        f"{summary['profit_factor']:.2f}"
    )
    print(
        f"{'Starting Capital':<28}: "
        f"RM{analytics['starting_capital']:,.2f}"
    )
    print(
        f"{'Ending Capital':<28}: "
        f"RM{analytics['ending_capital']:,.2f}"
    )
    print(
        f"{'Net Profit':<28}: "
        f"RM{analytics['net_profit']:,.2f}"
    )
    print(
        f"{'Compounded Growth':<28}: "
        f"{analytics['growth_pct']:.2f}%"
    )
    print(
        f"{'Peak Capital':<28}: "
        f"RM{analytics['peak_capital']:,.2f}"
    )
    print(
        f"{'Maximum Drawdown':<28}: "
        f"{analytics['maximum_drawdown_pct']:.2f}%"
    )
    print(
        f"{'Maximum Drawdown Amount':<28}: "
        f"RM{analytics['maximum_drawdown_amount']:,.2f}"
    )
    print(
        f"{'Maximum Drawdown Date':<28}: "
        f"{analytics['maximum_drawdown_date'] or 'N/A'}"
    )
    print(
        f"{'Current Drawdown':<28}: "
        f"{analytics['current_drawdown_pct']:.2f}%"
    )
    print(
        f"{'Recovery Factor':<28}: "
        f"{analytics['recovery_factor']:.2f}"
    )
