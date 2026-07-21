"""Tradable stock and ETF universe for Project Sentinel."""

STOCKS = {
    "AAPL": "Big Tech", "MSFT": "Big Tech", "NVDA": "AI",
    "META": "Big Tech", "AMZN": "Big Tech", "GOOGL": "Big Tech",
    "TSLA": "EV", "AMD": "AI", "AVGO": "Semiconductor",
    "PLTR": "AI", "SMCI": "AI", "ARM": "Semiconductor",
    "QCOM": "Semiconductor", "MU": "Semiconductor",
    "TSM": "Semiconductor", "AMAT": "Semiconductor",
    "LRCX": "Semiconductor", "KLAC": "Semiconductor",
    "ASML": "Semiconductor", "CRM": "Software", "ADBE": "Software",
    "ORCL": "Software", "NOW": "Software", "INTU": "Software",
    "SNOW": "Software", "CRWD": "Cybersecurity", "PANW": "Cybersecurity",
    "FTNT": "Cybersecurity", "ZS": "Cybersecurity", "MDB": "Cloud",
    "DDOG": "Cloud", "NET": "Cloud", "COST": "Consumer",
    "NFLX": "Consumer", "WMT": "Consumer", "JPM": "Finance",
    "V": "Finance", "MA": "Finance", "LLY": "Healthcare",
    "ABBV": "Healthcare",
}

ETFS = {
    # Broad market
    "SPY": "Broad Market", "QQQ": "Growth / Nasdaq 100",
    "IWM": "Small Cap", "DIA": "Dow Jones", "VTI": "Total US Market",
    # Sectors
    "XLK": "Technology", "XLC": "Communication Services",
    "XLY": "Consumer Discretionary", "XLP": "Consumer Staples",
    "XLF": "Financials", "XLV": "Healthcare", "XLI": "Industrials",
    "XLE": "Energy", "XLB": "Materials", "XLU": "Utilities",
    "XLRE": "Real Estate",
    # Industries / themes
    "SMH": "Semiconductors", "SOXX": "Semiconductors",
    "IGV": "Software", "HACK": "Cybersecurity", "CLOU": "Cloud",
    "XBI": "Biotechnology", "BOTZ": "Robotics & AI",
}

ASSET_UNIVERSE = {
    **{
        symbol: {"Asset Type": "STOCK", "Category": category}
        for symbol, category in STOCKS.items()
    },
    **{
        symbol: {"Asset Type": "ETF", "Category": category}
        for symbol, category in ETFS.items()
    },
}

TRADABLE_SYMBOLS = list(ASSET_UNIVERSE.keys())
ETF_SYMBOLS = list(ETFS.keys())
STOCK_SYMBOLS = list(STOCKS.keys())
