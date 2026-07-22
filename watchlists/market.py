"""Market instruments used to evaluate the trading environment.

These symbols provide context only. They are not automatically added to the
tradable stock/ETF opportunity universe.
"""

MARKET_SYMBOLS = {
    "SPY": "S&P 500",
    "QQQ": "Nasdaq 100",
    "IWM": "Russell 2000",
    "^VIX": "CBOE Volatility Index",
}

TREND_SYMBOLS = ("SPY", "QQQ", "IWM")
VOLATILITY_SYMBOL = "^VIX"
VIX_RISK_ON_LEVEL = 20.0
