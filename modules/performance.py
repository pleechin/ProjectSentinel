from __future__ import annotations

from typing import Any


def calculate_performance(trades: list[dict[str, Any]]) -> dict[str, float | int]:
    """
    Calculate performance statistics from a completed-trade journal.

    Expected trade fields:
        return_pct
        holding_days
    """

    total_trades = len(trades)

    returns = [
        float(trade["return_pct"])
        for trade in trades
    ]

    winning_returns = [
        value for value in returns
        if value > 0
    ]

    losing_returns = [
        value for value in returns
        if value <= 0
    ]

    wins = len(winning_returns)
    losses = len(losing_returns)

    total_return = sum(returns)

    win_rate = (
        wins / total_trades * 100
        if total_trades
        else 0.0
    )

    average_return = (
        total_return / total_trades
        if total_trades
        else 0.0
    )

    average_winner = (
        sum(winning_returns) / wins
        if wins
        else 0.0
    )

    average_loser = (
        sum(losing_returns) / losses
        if losses
        else 0.0
    )

    largest_winner = (
        max(winning_returns)
        if winning_returns
        else 0.0
    )

    largest_loser = (
        min(losing_returns)
        if losing_returns
        else 0.0
    )

    average_holding_days = (
        sum(
            int(trade["holding_days"])
            for trade in trades
        ) / total_trades
        if total_trades
        else 0.0
    )

    gross_profit = sum(winning_returns)
    gross_loss = abs(sum(losing_returns))

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else 0.0
    )

    expectancy = average_return

    return {
        "trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate, 2),
        "total_return": round(total_return, 2),
        "average_return": round(average_return, 2),
        "largest_winner": round(largest_winner, 2),
        "largest_loser": round(largest_loser, 2),
        "average_winner": round(average_winner, 2),
        "average_loser": round(average_loser, 2),
        "average_holding_days": round(average_holding_days, 2),
        "profit_factor": round(profit_factor, 2),
        "expectancy": round(expectancy, 2),
    }