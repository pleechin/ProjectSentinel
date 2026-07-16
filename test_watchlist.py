from config import WATCHLIST


print("=" * 55)
print("PROJECT SENTINEL WATCHLIST TEST")
print("=" * 55)

print(f"Number of stocks : {len(WATCHLIST)}")
print(f"Unique stocks    : {len(set(WATCHLIST))}")

duplicates = sorted(
    symbol
    for symbol in set(WATCHLIST)
    if WATCHLIST.count(symbol) > 1
)

if duplicates:
    print(f"Duplicates       : {', '.join(duplicates)}")
else:
    print("Duplicates       : None")

print()
print("STOCK SYMBOLS")
print("-" * 55)

for position, symbol in enumerate(WATCHLIST, start=1):
    print(f"{position:>2}. {symbol}")