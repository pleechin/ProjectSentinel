import pandas as pd
import yfinance as yf


def download_history(symbol, period="5y"):
    """
    Download historical price data.
    """

    print(f"Downloading {symbol}...")

    data = yf.download(
        symbol,
        period=period,
        auto_adjust=True,
        progress=False,
    )

    # Normalize MultiIndex columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(-1)

    return data