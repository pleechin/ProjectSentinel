from typing import Any


def build_equity_curve(
    trades: list[dict[str, Any]],
    starting_capital: float = 100000,
) -> list[dict[str, Any]]:
    """
    Build an equity curve using compounded returns.
    """

    capital = starting_capital
    equity_curve = []

    for trade in trades:

        capital *= (1 + trade["return_pct"] / 100)

        equity_curve.append(
            {
                "date": trade["sell_date"],
                "capital": round(capital, 2),
                "return_pct": trade["return_pct"],
            }
        )

    return equity_curve