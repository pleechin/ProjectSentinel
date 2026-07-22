from modules.explainability import build_explanation

score = {
    "Market Component": 13, "Sector Component": 15, "Industry Component": 12,
    "Trend Component": 20, "Momentum Component": 8, "Volume Component": 7,
    "Risk Component": 12, "Positive Factors": ["Strong market", "Strong trend"],
    "Warnings": ["Volume could improve"],
}
stock = {"Sector Name": "Technology", "Industry Name": "Semiconductors"}
result = build_explanation(score, stock)
assert len(result["Score Breakdown"]) == 7
assert result["Strongest Component"] in {"Sector", "Trend"}
assert "Technology" in result["Context Summary"]
print("Explainability tests passed.")
