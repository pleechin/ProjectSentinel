import yfinance as yf


def download_history(symbol, period="5y"):
    """
    Download historical price data for a stock.
    """

    print(f"Downloading {symbol}...")

    data = yf.download(
        symbol,
        period=period,
        progress=False,
        auto_adjust=True,
    )

    return data