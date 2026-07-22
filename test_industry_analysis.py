import pandas as pd

from modules.industry_analysis import get_industry_leadership
from watchlists.industry_etfs import INDUSTRY_BENCHMARK, INDUSTRY_ETFS


def history(start: float, step: float, rows: int = 100) -> pd.DataFrame:
    return pd.DataFrame({"Close": [start + (step * index) for index in range(rows)]})


def loader(symbol: str):
    if symbol == INDUSTRY_BENCHMARK:
        return history(100.0, 0.20)
    symbols = list(INDUSTRY_ETFS.values())
    position = symbols.index(symbol)
    if position == 0:
        return history(100.0, 0.70)
    if position == 1:
        return history(100.0, 0.40)
    if position == symbols[-1]:
        return history(150.0, -0.20)
    return history(100.0, 0.15)


result = get_industry_leadership(loader)
assert result["status"] == "READY"
assert len(result["rankings"]) == len(INDUSTRY_ETFS)
assert result["rankings"][0]["Rank"] == 1
assert result["rankings"][0]["Industry"] == list(INDUSTRY_ETFS.keys())[0]
assert 0 <= result["rankings"][0]["Industry Score"] <= 100
assert result["leaders"]
assert result["laggards"]

no_data = get_industry_leadership(lambda symbol: None)
assert no_data["status"] == "NO_DATA"
assert no_data["rankings"] == []

print("Industry intelligence tests passed.")
