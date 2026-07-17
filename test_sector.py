from config import WATCHLIST
from modules.market import analyse_market
from modules.scanner import scan_watchlist
from modules.sector import calculate_sector_strength

market = analyse_market()

results = scan_watchlist(market)

summary = calculate_sector_strength(
    results,
    WATCHLIST,
)

print("=" * 60)
print("SECTOR STRENGTH")
print("=" * 60)

for sector in summary:

    print(
        f"{sector['Sector']:<18}"
        f"{sector['Average Score']:>6}"
        f"   ({sector['Stocks']} stocks)"
    )