from config import WATCHLIST

print("=" * 55)
print("PROJECT SENTINEL WATCHLIST TEST")
print("=" * 55)

print(f"Number of stocks : {len(WATCHLIST)}")

print()
print("STOCK SYMBOLS")
print("-" * 55)

for position, (symbol, sector) in enumerate(WATCHLIST.items(), start=1):
    print(f"{position:>2}. {symbol:<6} {sector}")