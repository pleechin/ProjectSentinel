from config import WATCHLIST_SYMBOLS
from modules.backtester import (
    download_history,
    run_backtest,
)


def run_portfolio_backtest():
    """
    Backtest every stock in the watchlist.
    """

    results = []

    for symbol in WATCHLIST_SYMBOLS:

        print(f"\nTesting {symbol}...")

        history = download_history(symbol)

        result = run_backtest(history)

        results.append({
            "symbol": symbol,
            **result["summary"],
        })

    results.sort(
        key=lambda x: x["total_return"],
        reverse=True,
    )

    return results