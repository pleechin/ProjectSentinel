from __future__ import annotations

from typing import Any


def calculate_equity_analytics(
    equity_curve: list[dict[str, Any]],
    starting_capital: float = 100000.0,
) -> dict[str, float | str | None]:
    """
    Calculate portfolio-level analytics from a completed-trade equity curve.

    Expected equity-curve fields:
        date
        capital
    """

    if starting_capital <= 0:
        raise ValueError("starting_capital must be greater than zero")

    if not equity_curve:
        return {
            "starting_capital": round(starting_capital, 2),
            "ending_capital": round(starting_capital, 2),
            "net_profit": 0.0,
            "growth_pct": 0.0,
            "peak_capital": round(starting_capital, 2),
            "maximum_drawdown_pct": 0.0,
            "maximum_drawdown_amount": 0.0,
            "maximum_drawdown_date": None,
            "current_drawdown_pct": 0.0,
            "recovery_factor": 0.0,
        }

    ending_capital = float(equity_curve[-1]["capital"])
    peak_capital = starting_capital
    maximum_drawdown_pct = 0.0
    maximum_drawdown_amount = 0.0
    maximum_drawdown_date = None

    for row in equity_curve:
        capital = float(row["capital"])

        if capital > peak_capital:
            peak_capital = capital

        drawdown_amount = peak_capital - capital
        drawdown_pct = (
            drawdown_amount / peak_capital * 100
            if peak_capital > 0
            else 0.0
        )

        if drawdown_pct > maximum_drawdown_pct:
            maximum_drawdown_pct = drawdown_pct
            maximum_drawdown_amount = drawdown_amount
            maximum_drawdown_date = str(row["date"])

    net_profit = ending_capital - starting_capital
    growth_pct = net_profit / starting_capital * 100

    current_drawdown_pct = (
        (peak_capital - ending_capital) / peak_capital * 100
        if peak_capital > 0
        else 0.0
    )

    recovery_factor = (
        net_profit / maximum_drawdown_amount
        if maximum_drawdown_amount > 0
        else 0.0
    )

    return {
        "starting_capital": round(starting_capital, 2),
        "ending_capital": round(ending_capital, 2),
        "net_profit": round(net_profit, 2),
        "growth_pct": round(growth_pct, 2),
        "peak_capital": round(peak_capital, 2),
        "maximum_drawdown_pct": round(maximum_drawdown_pct, 2),
        "maximum_drawdown_amount": round(maximum_drawdown_amount, 2),
        "maximum_drawdown_date": maximum_drawdown_date,
        "current_drawdown_pct": round(current_drawdown_pct, 2),
        "recovery_factor": round(recovery_factor, 2),
    }
