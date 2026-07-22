"""Map Sentinel assets to their sector and industry intelligence groups."""

CATEGORY_TO_SECTOR = {
    "Big Tech": "Technology", "AI": "Technology", "Semiconductor": "Technology",
    "Software": "Technology", "Cybersecurity": "Technology", "Cloud": "Technology",
    "EV": "Consumer Discretionary", "Consumer": "Consumer Discretionary",
    "Finance": "Financials", "Healthcare": "Healthcare",
}

CATEGORY_TO_INDUSTRY = {
    "AI": "Robotics & AI", "Semiconductor": "Semiconductors",
    "Software": "Software", "Cybersecurity": "Cybersecurity",
    "Cloud": "Cloud Computing",
}

SECTOR_ETF_TO_NAME = {
    "XLK": "Technology", "XLC": "Communication Services", "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples", "XLF": "Financials", "XLV": "Healthcare",
    "XLI": "Industrials", "XLE": "Energy", "XLB": "Materials", "XLU": "Utilities",
    "XLRE": "Real Estate",
}

INDUSTRY_ETF_TO_NAME = {
    "SMH": "Semiconductors", "SOXX": "Semiconductors", "IGV": "Software",
    "HACK": "Cybersecurity", "CLOU": "Cloud Computing", "XBI": "Biotechnology",
    "BOTZ": "Robotics & AI",
}


def resolve_asset_context(symbol: str, category: str) -> tuple[str | None, str | None]:
    """Return the most relevant sector and industry names for an asset."""
    sector = SECTOR_ETF_TO_NAME.get(symbol) or CATEGORY_TO_SECTOR.get(category)
    industry = INDUSTRY_ETF_TO_NAME.get(symbol) or CATEGORY_TO_INDUSTRY.get(category)
    return sector, industry


def lookup_context_score(snapshot: dict | None, name: str | None, label_key: str, score_key: str) -> tuple[int, str]:
    """Find one named score in a sector/industry snapshot."""
    if not snapshot or not name:
        return 50, "UNMAPPED"
    for item in snapshot.get("rankings", []):
        if str(item.get(label_key, "")).lower() == name.lower():
            return int(item.get(score_key, 0)), str(item.get("Status", "UNKNOWN"))
    return 50, "NO DATA"
