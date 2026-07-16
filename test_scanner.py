from modules.market import analyse_market
from modules.scanner import scan_watchlist


market = analyse_market()
results = scan_watchlist(market)

print("=" * 72)
print("PROJECT SENTINEL SCANNER TEST")
print("=" * 72)

print(f"Market score  : {market['Score']:.0f}/100")
print(f"Market status : {market['Status']}")

if results.empty:
    print("No stocks were successfully analysed.")
else:
    print("\nRANKED STOCKS")
    print("=" * 72)

    for position, row in results.iterrows():
        print(f"\n#{position + 1} — {row['Symbol']}")
        print("-" * 45)
        print(f"Decision      : {row['Decision']}")
        print(f"Health        : {row['Health']}")
        print(f"Total score   : {row['Total Score']}/100")
        print(f"Trend         : {row['Trend']}")
        print(f"Entry score   : {row['Entry Score']}/100")
        print(f"Reward:risk   : {row['Reward Risk']:.2f}R")
        print(f"Position size : {int(row['Position Size'])} shares")