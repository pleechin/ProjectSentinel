import pandas as pd

from modules.sector_analysis import get_sector_rotation
from watchlists.sector_etfs import SECTOR_BENCHMARK, SECTOR_ETFS


def history(start: float, daily_step: float, rows: int = 100) -> pd.DataFrame:
    closes = [start + daily_step * index for index in range(rows)]
    return pd.DataFrame({"Close": closes})


def fake_loader(symbol: str) -> pd.DataFrame:
    if symbol == SECTOR_BENCHMARK:
        return history(100.0, 0.25)
    order = list(SECTOR_ETFS.values()).index(symbol)
    # Earlier sectors intentionally outperform the benchmark more strongly.
    return history(100.0, 0.45 - order * 0.04)


def main() -> None:
    result = get_sector_rotation(fake_loader)
    assert result["status"] == "READY"
    assert result["benchmark"] == "SPY"
    assert len(result["rankings"]) == len(SECTOR_ETFS)
    assert len(result["leaders"]) == 3
    assert result["rankings"][0]["Rank"] == 1
    assert result["rankings"][0]["Sector Score"] >= result["rankings"][-1]["Sector Score"]
    assert {item["Status"] for item in result["rankings"]}.issubset(
        {"LEADING", "STRONG", "NEUTRAL", "WEAK", "NO DATA"}
    )

    no_data = get_sector_rotation(lambda _symbol: None)
    assert no_data["status"] == "NO_DATA"
    assert no_data["rankings"] == []

    print("Sector rotation tests passed.")


if __name__ == "__main__":
    main()
