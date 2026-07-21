# ==========================================
# Project Sentinel Configuration
# ==========================================
from watchlists.tradable_assets import ASSET_UNIVERSE, ETF_SYMBOLS, STOCK_SYMBOLS, TRADABLE_SYMBOLS

# Backward-compatible name used by the scanner.
WATCHLIST_SYMBOLS = TRADABLE_SYMBOLS

# Account
ACCOUNT_SIZE_RM = 20000
RISK_PERCENT = 1.0
USD_MYR_RATE = 4.30

# Trading Rules
SUPPORT_LOOKBACK = 10
RESISTANCE_LOOKBACK = 20
STOP_BUFFER_PERCENT = 0.5
ENTRY_BUFFER_PERCENT = 0.1
ATR_PERIOD = 14
ATR_MULTIPLIER = 2.0
EMA20 = 20
EMA50 = 50
EMA200 = 200
MIN_VOLUME_RATIO = 1.20
MIN_REWARD_RISK = 2.0
MAX_ACCEPTABLE_STOP_PERCENT = 8.0

# Market context remains separate from tradable ETF opportunities.
MARKET_INDEX = ["SPY", "QQQ"]
