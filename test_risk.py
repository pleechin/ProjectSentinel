import pandas as pd
import yfinance as yf

from config import ATR_PERIOD
from modules.risk import calculate_trade_plan


history = yf.Ticker("AAPL").history(
    period="1y",
    interval="1d",
)

history = history.dropna(
    subset=["Open", "High", "Low", "Close", "Volume"]
).copy()

previous_close = history["Close"].shift(1)

true_range = pd.concat(
    [
        history["High"] - history["Low"],
        (history["High"] - previous_close).abs(),
        (history["Low"] - previous_close).abs(),
    ],
    axis=1,
).max(axis=1)

history["ATR14"] = true_range.ewm(
    alpha=1 / ATR_PERIOD,
    adjust=False,
).mean()

plan = calculate_trade_plan(history)

print("=" * 55)
print("AAPL RISK MODULE TEST")
print("=" * 55)

print(f"Suggested entry  : ${plan['Suggested Entry']:.2f}")
print(f"Recent support   : ${plan['Support']:.2f}")
print(f"Swing stop       : ${plan['Swing Stop']:.2f}")
print(f"ATR value        : ${plan['ATR Value']:.2f}")
print(f"ATR stop         : ${plan['ATR Stop']:.2f}")
print(f"Recommended stop : ${plan['Recommended Stop']:.2f}")
print(f"Stop method      : {plan['Stop Method']}")
print(
    f"Stop distance    : "
    f"${plan['Stop Distance']:.2f} "
    f"({plan['Stop Distance %']:.2f}%)"
)
print(f"Resistance       : ${plan['Resistance']:.2f}")
print(f"Reward-to-risk   : {plan['Reward Risk']:.2f}R")
print(f"Position size    : {plan['Position Size']} shares")
print(f"Position value   : RM{plan['Position Value RM']:,.2f}")
print(f"Estimated loss   : RM{plan['Estimated Loss RM']:,.2f}")
print(f"Estimated profit : RM{plan['Estimated Profit RM']:,.2f}")
print(f"Risk passes      : {plan['Risk Passes']}")
print(f"Warnings         : {plan['Warnings']}")