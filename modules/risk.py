from __future__ import annotations

from config import (
    ACCOUNT_SIZE_RM,
    ATR_MULTIPLIER,
    ATR_PERIOD,
    ENTRY_BUFFER_PERCENT,
    MAX_ACCEPTABLE_STOP_PERCENT,
    MIN_REWARD_RISK,
    RESISTANCE_LOOKBACK,
    RISK_PERCENT,
    STOP_BUFFER_PERCENT,
    SUPPORT_LOOKBACK,
    USD_MYR_RATE,
)


def calculate_trade_plan(history) -> dict:
    """Calculate entry, stop, target, R:R and position size."""

    if history.empty:
        raise ValueError("history must not be empty")

    atr_column = f"ATR{ATR_PERIOD}"
    if atr_column not in history.columns:
        raise KeyError(
            f"Required column '{atr_column}' is missing"
        )

    latest = history.iloc[-1]
    latest_high = float(latest["High"])
    atr_value = float(latest[atr_column])

    suggested_entry = latest_high * (
        1 + ENTRY_BUFFER_PERCENT / 100
    )

    recent_support = float(
        history["Low"].tail(SUPPORT_LOOKBACK).min()
    )
    swing_stop = recent_support * (
        1 - STOP_BUFFER_PERCENT / 100
    )
    atr_stop = suggested_entry - (
        atr_value * ATR_MULTIPLIER
    )

    recommended_stop = min(
        swing_stop,
        atr_stop,
    )

    if recommended_stop == swing_stop:
        stop_method = (
            f"Swing support: lowest low of last "
            f"{SUPPORT_LOOKBACK} sessions minus "
            f"{STOP_BUFFER_PERCENT:.1f}%"
        )
    else:
        stop_method = (
            f"ATR stop: entry minus "
            f"{ATR_MULTIPLIER:.1f} × ATR{ATR_PERIOD}"
        )

    stop_distance = suggested_entry - recommended_stop
    stop_distance_percent = (
        stop_distance / suggested_entry * 100
        if suggested_entry > 0
        else 0.0
    )

    recent_resistance = float(
        history["High"].tail(RESISTANCE_LOOKBACK).max()
    )
    potential_reward = recent_resistance - suggested_entry

    reward_risk_ratio = (
        potential_reward / stop_distance
        if stop_distance > 0 and potential_reward > 0
        else 0.0
    )

    maximum_risk_rm = ACCOUNT_SIZE_RM * RISK_PERCENT / 100
    maximum_risk_usd = maximum_risk_rm / USD_MYR_RATE

    shares_by_risk = (
        int(maximum_risk_usd / stop_distance)
        if stop_distance > 0
        else 0
    )

    account_size_usd = ACCOUNT_SIZE_RM / USD_MYR_RATE
    shares_by_cash = (
        int(account_size_usd / suggested_entry)
        if suggested_entry > 0
        else 0
    )

    position_size = max(
        min(shares_by_risk, shares_by_cash),
        0,
    )

    position_value_rm = (
        position_size * suggested_entry * USD_MYR_RATE
    )
    estimated_loss_rm = (
        position_size * stop_distance * USD_MYR_RATE
    )
    estimated_profit_rm = (
        position_size
        * max(potential_reward, 0)
        * USD_MYR_RATE
    )

    warnings: list[str] = []

    if reward_risk_ratio < MIN_REWARD_RISK:
        warnings.append(
            f"Reward-to-risk is below {MIN_REWARD_RISK:.1f}R"
        )

    if stop_distance_percent > MAX_ACCEPTABLE_STOP_PERCENT:
        warnings.append(
            f"Stop distance exceeds "
            f"{MAX_ACCEPTABLE_STOP_PERCENT:.1f}%"
        )

    if suggested_entry >= recent_resistance:
        warnings.append(
            "Suggested entry is at or above resistance"
        )

    if position_size < 1:
        warnings.append(
            "Account risk permits fewer than one share"
        )

    risk_passes = (
        reward_risk_ratio >= MIN_REWARD_RISK
        and 0 < stop_distance_percent
        <= MAX_ACCEPTABLE_STOP_PERCENT
        and position_size >= 1
        and suggested_entry < recent_resistance
    )

    return {
        "Suggested Entry": suggested_entry,
        "Support": recent_support,
        "Swing Stop": swing_stop,
        "ATR Value": atr_value,
        "ATR Stop": atr_stop,
        "Recommended Stop": recommended_stop,
        "Stop Method": stop_method,
        "Stop Distance": stop_distance,
        "Stop Distance %": stop_distance_percent,
        "Resistance": recent_resistance,
        "Potential Reward": potential_reward,
        "Reward Risk": reward_risk_ratio,
        "Position Size": position_size,
        "Position Value RM": position_value_rm,
        "Estimated Loss RM": estimated_loss_rm,
        "Estimated Profit RM": estimated_profit_rm,
        "Risk Passes": risk_passes,
        "Warnings": (
            ", ".join(warnings)
            if warnings
            else "No major risk warnings"
        ),
    }
