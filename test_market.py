from modules.market import analyse_market

market = analyse_market()

print("=" * 50)
print("US MARKET TEST")
print("=" * 50)

print(f"Combined score : {market['Score']:.0f}/100")
print(f"Status         : {market['Status']}")
print(f"Permission     : {market['Permission']}")

for item in market["Results"]:
    print()
    print(f"Symbol      : {item['Symbol']}")
    print(f"Score       : {item['Score']}/100")
    print(f"Explanation : {item['Reasons']}")