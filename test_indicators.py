import yfinance as yf

from indicators.atr import add_atr
from indicators.ema import add_ema
from indicators.volume import add_average_volume


history = yf.Ticker("AAPL").history(
    period="1y",
    interval="1d",
)

history = history.dropna(
    subset=["Open", "High", "Low", "Close", "Volume"]
).copy()

history = add_ema(history)
history = add_atr(history, period=14)
history = add_average_volume(history, period=20)

latest = history.iloc[-1]

print("=" * 55)
print("SHARED INDICATOR TEST")
print("=" * 55)
print(f"Close            : ${latest['Close']:.2f}")
print(f"EMA20            : ${latest['EMA20']:.2f}")
print(f"EMA50            : ${latest['EMA50']:.2f}")
print(f"EMA200           : ${latest['EMA200']:.2f}")
print(f"ATR14            : ${latest['ATR14']:.2f}")
print(f"Average volume20 : {latest['AverageVolume20']:,.0f}")