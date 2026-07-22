"""Backward-compatible market module.

Market-context implementation moved to ``modules.market_context`` in Sprint
12.1. Existing imports of ``modules.market.analyse_market`` continue to work.
"""

from modules.market_context import analyse_market, download_market_history, get_market_context

# Legacy alias retained for code that imported this helper directly.
prepare_market_history = download_market_history

__all__ = [
    "analyse_market",
    "download_market_history",
    "get_market_context",
    "prepare_market_history",
]
