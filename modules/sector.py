from collections import defaultdict


def calculate_sector_strength(results, watchlist):
    """
    Calculate the average score for each sector.
    """

    sectors = defaultdict(list)

    for _, row in results.iterrows():

        symbol = row["Symbol"]

        sector = watchlist.get(symbol, "Unknown")

        sectors[sector].append(
            row["Total Score"]
        )

    summary = []

    for sector, scores in sectors.items():

        average = sum(scores) / len(scores)

        summary.append(
            {
                "Sector": sector,
                "Stocks": len(scores),
                "Average Score": round(average, 1),
            }
        )

    summary.sort(
        key=lambda item: item["Average Score"],
        reverse=True,
    )

    return summary