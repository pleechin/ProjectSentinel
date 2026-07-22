from modules.score import calculate_score

market = {"Score": 80, "Status": "BULLISH", "Permission": True}
stock = {
    "Trend": "STRONG BULLISH", "Bullish Candle": True, "EMA20 Distance %": 1.0,
    "Volume Ratio": 1.5, "Sector Name": "Technology", "Sector Score": 100,
    "Industry Name": "Semiconductors", "Industry Score": 80,
}
plan = {"Reward Risk": 3.0, "Stop Distance %": 5.0, "Position Size": 3}
result = calculate_score(market, stock, plan)
assert 0 <= result["Score"] <= 100
assert result["Sector Component"] == 15
assert result["Industry Component"] == 12
assert result["Score"] >= 80
print("Context-aware scoring tests passed.")
