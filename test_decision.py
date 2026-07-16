
from modules.decision import evaluate_trade


market = {
    "Score": 88,
    "Status": "HEALTHY",
    "Permission": True,
}

stock = {
    "Trend": "BULLISH",
    "Entry Score": 80,
    "Bullish Candle": True,
    "Volume Ratio": 1.35,
    "EMA20 Distance %": 0.80,
}

trade_plan = {
    "Reward Risk": 2.40,
    "Stop Distance %": 5.20,
    "Position Size": 4,
    "Risk Passes": True,
}

decision = evaluate_trade(
    market=market,
    stock=stock,
    trade_plan=trade_plan,
)

print("=" * 60)
print("PROJECT SENTINEL DECISION TEST")
print("=" * 60)

print(f"Decision          : {decision['Decision']}")
print(f"Health            : {decision['Health']}")
print(f"Total score       : {decision['Total Score']}/100")
print(
    f"Market component  : "
    f"{decision['Market Component']}/20"
)
print(
    f"Trend component   : "
    f"{decision['Trend Component']}/30"
)
print(
    f"Entry component   : "
    f"{decision['Entry Component']}/30"
)
print(
    f"Risk component    : "
    f"{decision['Risk Component']}/20"
)

print("\nPOSITIVE FACTORS")
for item in decision["Positive Factors"]:
    print(f"  + {item}")

print("\nWARNINGS")
if decision["Warnings"]:
    for item in decision["Warnings"]:
        print(f"  - {item}")
else:
    print("  - No major warnings")

print("\nNEXT ACTION")
for item in decision["Next Action"]:
    print(f"  > {item}")