import pandas as pd
import yfinance as yf

# ============================================================
# Settings
# ============================================================

WATCHLIST = [
    "AAPL",
    "MSFT",
    "NVDA",
    "META",
    "AMZN",
    "GOOGL",
    "AVGO",
    "AMD",
    "PLTR",
    "TSLA",
]

MARKET_SYMBOLS = ["SPY", "QQQ"]

ACCOUNT_SIZE_RM = 20_000
RISK_PERCENT = 1.0
USD_MYR_RATE = 4.30  # Temporary manual estimate

SUPPORT_LOOKBACK = 10
RESISTANCE_LOOKBACK = 20

STOP_BUFFER_PERCENT = 0.5
ENTRY_BUFFER_PERCENT = 0.1

ATR_PERIOD = 14
ATR_MULTIPLIER = 2.0

MAX_STOP_DISTANCE_PERCENT = 8.0
MINIMUM_REWARD_RISK = 2.0


# ============================================================
# Shared indicator calculations
# ============================================================

def prepare_history(symbol: str) -> pd.DataFrame | None:
    """Download and prepare one year of daily market data."""

    try:
        history = yf.Ticker(symbol).history(
            period="1y",
            interval="1d",
        )

        if history.empty:
            print(f"{symbol}: No data returned")
            return None

        history = history.dropna(
            subset=["Open", "High", "Low", "Close", "Volume"]
        ).copy()

        if len(history) < 60:
            print(f"{symbol}: Not enough historical data")
            return None

        history["EMA20"] = history["Close"].ewm(
            span=20,
            adjust=False,
        ).mean()

        history["EMA50"] = history["Close"].ewm(
            span=50,
            adjust=False,
        ).mean()

        history["EMA200"] = history["Close"].ewm(
            span=200,
            adjust=False,
        ).mean()

        history["AverageVolume20"] = history["Volume"].rolling(
            window=20,
        ).mean()

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

        return history

    except Exception as error:
        print(f"{symbol}: Data error — {error}")
        return None


# ============================================================
# Market filter
# ============================================================

def analyse_market() -> dict:
    """
    Analyse SPY and QQQ.

    Each index ETF receives:
    - 25 points if close is above EMA20
    - 25 points if EMA20 is above EMA50
    - 25 points if close is above EMA200
    - 25 points if EMA50 is rising
    """

    market_results = []
    total_market_score = 0

    for symbol in MARKET_SYMBOLS:
        history = prepare_history(symbol)

        if history is None:
            continue

        latest = history.iloc[-1]
        previous = history.iloc[-6]

        close_price = float(latest["Close"])
        ema20 = float(latest["EMA20"])
        ema50 = float(latest["EMA50"])
        ema200 = float(latest["EMA200"])

        previous_ema50 = float(previous["EMA50"])

        score = 0
        reasons = []

        if close_price > ema20:
            score += 25
            reasons.append("Price above EMA20")
        else:
            reasons.append("Price below EMA20")

        if ema20 > ema50:
            score += 25
            reasons.append("EMA20 above EMA50")
        else:
            reasons.append("EMA20 below EMA50")

        if close_price > ema200:
            score += 25
            reasons.append("Price above EMA200")
        else:
            reasons.append("Price below EMA200")

        if ema50 > previous_ema50:
            score += 25
            reasons.append("EMA50 is rising")
        else:
            reasons.append("EMA50 is flat or falling")

        total_market_score += score

        market_results.append(
            {
                "Symbol": symbol,
                "Close": close_price,
                "EMA20": ema20,
                "EMA50": ema50,
                "EMA200": ema200,
                "Score": score,
                "Reasons": ", ".join(reasons),
            }
        )

    if not market_results:
        return {
            "Score": 0,
            "Status": "UNKNOWN",
            "Permission": False,
            "Results": [],
        }

    maximum_score = len(market_results) * 100

    market_score_percent = (
        total_market_score / maximum_score
    ) * 100

    if market_score_percent >= 75:
        market_status = "HEALTHY"
        allow_candidates = True

    elif market_score_percent >= 50:
        market_status = "CAUTION"
        allow_candidates = True

    else:
        market_status = "UNHEALTHY"
        allow_candidates = False

    return {
        "Score": market_score_percent,
        "Status": market_status,
        "Permission": allow_candidates,
        "Results": market_results,
    }


# ============================================================
# Individual stock analysis
# ============================================================

def analyse_stock(
    symbol: str,
    market_status: str,
    market_permission: bool,
) -> dict | None:
    """Analyse one stock for a possible long swing trade."""

    history = prepare_history(symbol)

    if history is None:
        return None

    try:
        latest = history.iloc[-1]

        open_price = float(latest["Open"])
        high_price = float(latest["High"])
        close_price = float(latest["Close"])

        ema20 = float(latest["EMA20"])
        ema50 = float(latest["EMA50"])
        ema200 = float(latest["EMA200"])

        current_volume = float(latest["Volume"])
        average_volume = float(latest["AverageVolume20"])
        atr14 = float(latest["ATR14"])

        # ----------------------------------------------------
        # Trend, candle and volume
        # ----------------------------------------------------

        distance_from_ema20 = (
            (close_price - ema20) / ema20
        ) * 100

        volume_ratio = (
            current_volume / average_volume
            if average_volume > 0
            else 0
        )

        bullish_candle = close_price > open_price

        if close_price > ema20 > ema50 > ema200:
            trend = "STRONG BULLISH"

        elif close_price > ema20 > ema50:
            trend = "BULLISH"

        elif close_price < ema20 < ema50:
            trend = "BEARISH"

        else:
            trend = "MIXED"

        # ----------------------------------------------------
        # Entry
        # ----------------------------------------------------

        suggested_entry = high_price * (
            1 + ENTRY_BUFFER_PERCENT / 100
        )

        # ----------------------------------------------------
        # Stop-loss methods
        # ----------------------------------------------------

        recent_support = float(
            history["Low"]
            .tail(SUPPORT_LOOKBACK)
            .min()
        )

        swing_stop = recent_support * (
            1 - STOP_BUFFER_PERCENT / 100
        )

        atr_stop = suggested_entry - (
            atr14 * ATR_MULTIPLIER
        )

        recommended_stop = min(
            swing_stop,
            atr_stop,
        )

        if recommended_stop == swing_stop:
            selected_stop_method = (
                f"Swing support: lowest low of last "
                f"{SUPPORT_LOOKBACK} sessions minus "
                f"{STOP_BUFFER_PERCENT:.1f}%"
            )
        else:
            selected_stop_method = (
                f"ATR stop: entry minus "
                f"{ATR_MULTIPLIER:.1f} × ATR{ATR_PERIOD}"
            )

        stop_distance = suggested_entry - recommended_stop

        stop_distance_percent = (
            stop_distance / suggested_entry
        ) * 100

        # ----------------------------------------------------
        # Target and reward-to-risk
        # ----------------------------------------------------

        recent_resistance = float(
            history["High"]
            .tail(RESISTANCE_LOOKBACK)
            .max()
        )

        potential_reward = (
            recent_resistance - suggested_entry
        )

        if stop_distance > 0 and potential_reward > 0:
            reward_risk_ratio = (
                potential_reward / stop_distance
            )
        else:
            reward_risk_ratio = 0

        # ----------------------------------------------------
        # Entry score
        # ----------------------------------------------------

        entry_score = 0
        positive_reasons = []
        warnings = []

        if trend in ["BULLISH", "STRONG BULLISH"]:
            entry_score += 40
            positive_reasons.append("Bullish EMA trend")

        if -1.0 <= distance_from_ema20 <= 2.0:
            entry_score += 25
            positive_reasons.append("Price is near EMA20")

        if bullish_candle:
            entry_score += 15
            positive_reasons.append("Latest candle is bullish")

        if volume_ratio >= 1.20:
            entry_score += 20
            positive_reasons.append(
                "Volume is at least 1.2x average"
            )

        # ----------------------------------------------------
        # Position sizing
        # ----------------------------------------------------

        maximum_risk_rm = (
            ACCOUNT_SIZE_RM * RISK_PERCENT / 100
        )

        maximum_risk_usd = (
            maximum_risk_rm / USD_MYR_RATE
        )

        if stop_distance > 0:
            shares_by_risk = int(
                maximum_risk_usd / stop_distance
            )
        else:
            shares_by_risk = 0

        account_size_usd = (
            ACCOUNT_SIZE_RM / USD_MYR_RATE
        )

        if suggested_entry > 0:
            shares_by_cash = int(
                account_size_usd / suggested_entry
            )
        else:
            shares_by_cash = 0

        position_size = min(
            shares_by_risk,
            shares_by_cash,
        )

        position_value_rm = (
            position_size
            * suggested_entry
            * USD_MYR_RATE
        )

        estimated_loss_rm = (
            position_size
            * stop_distance
            * USD_MYR_RATE
        )

        estimated_profit_rm = (
            position_size
            * max(potential_reward, 0)
            * USD_MYR_RATE
        )

        # ----------------------------------------------------
        # Warnings and final decision
        # ----------------------------------------------------

        if market_status == "CAUTION":
            warnings.append(
                "Wider market is in CAUTION condition"
            )

        if market_status == "UNHEALTHY":
            warnings.append(
                "Wider market does not support new long trades"
            )

        if reward_risk_ratio < MINIMUM_REWARD_RISK:
            warnings.append(
                f"Reward-to-risk is below "
                f"{MINIMUM_REWARD_RISK:.1f}R"
            )

        if stop_distance_percent > MAX_STOP_DISTANCE_PERCENT:
            warnings.append(
                f"Stop distance exceeds "
                f"{MAX_STOP_DISTANCE_PERCENT:.1f}%"
            )

        if suggested_entry >= recent_resistance:
            warnings.append(
                "Suggested entry is at or above resistance"
            )

        if position_size < 1:
            warnings.append(
                "Account risk permits fewer than one share"
            )

        candidate_passes = (
            market_permission
            and market_status == "HEALTHY"
            and entry_score >= 80
            and reward_risk_ratio >= MINIMUM_REWARD_RISK
            and trend in ["BULLISH", "STRONG BULLISH"]
            and stop_distance_percent <= MAX_STOP_DISTANCE_PERCENT
            and position_size >= 1
        )

        watch_passes = (
            market_permission
            and entry_score >= 60
        )

        if candidate_passes:
            status = "CANDIDATE"

        elif watch_passes:
            status = "WATCH"

        else:
            status = "WAIT"

        return {
            "Symbol": symbol,
            "Data Date": history.index[-1].date(),
            "Market Status": market_status,

            "Close": close_price,
            "EMA20": ema20,
            "EMA50": ema50,
            "EMA200": ema200,
            "EMA20 Distance %": distance_from_ema20,
            "Volume Ratio": volume_ratio,
            "Trend": trend,
            "Bullish Candle": bullish_candle,

            "Entry Score": entry_score,
            "Suggested Entry": suggested_entry,

            "Support": recent_support,
            "Swing Stop": swing_stop,
            "ATR14": atr14,
            "ATR Stop": atr_stop,
            "Recommended Stop": recommended_stop,
            "Stop Method": selected_stop_method,
            "Stop Distance": stop_distance,
            "Stop Distance %": stop_distance_percent,

            "Resistance": recent_resistance,
            "Potential Reward": potential_reward,
            "Reward Risk": reward_risk_ratio,

            "Position Size": position_size,
            "Position Value RM": position_value_rm,
            "Estimated Loss RM": estimated_loss_rm,
            "Estimated Profit RM": estimated_profit_rm,

            "Status": status,
            "Positive Reasons": (
                ", ".join(positive_reasons)
                if positive_reasons
                else "No positive entry conditions passed"
            ),
            "Warnings": (
                ", ".join(warnings)
                if warnings
                else "No major warnings"
            ),
        }

    except Exception as error:
        print(f"{symbol}: Analysis error — {error}")
        return None


# ============================================================
# Run market filter
# ============================================================

print("=" * 78)
print("Project Sentinel v0.5 — US Market Filter")
print("=" * 78)

market = analyse_market()

print("\nUS MARKET CONDITION")
print("-" * 50)

for item in market["Results"]:
    print(f"\n{item['Symbol']}")
    print(f"Close       : ${item['Close']:.2f}")
    print(f"EMA20       : ${item['EMA20']:.2f}")
    print(f"EMA50       : ${item['EMA50']:.2f}")
    print(f"EMA200      : ${item['EMA200']:.2f}")
    print(f"Market score: {item['Score']}/100")
    print(f"Explanation : {item['Reasons']}")

print("\n" + "-" * 50)
print(f"Combined market score : {market['Score']:.0f}/100")
print(f"Market status         : {market['Status']}")

if market["Permission"]:
    print("Long-trade scanning   : ALLOWED")
else:
    print("Long-trade scanning   : BLOCKED")

# ============================================================
# Run stock scanner
# ============================================================

print("\n" + "=" * 78)
print("SCANNING WATCHLIST")
print("=" * 78)

results = []

for symbol in WATCHLIST:
    print(f"Scanning {symbol}...")

    result = analyse_stock(
        symbol=symbol,
        market_status=market["Status"],
        market_permission=market["Permission"],
    )

    if result is not None:
        results.append(result)

if not results:
    print("No stocks were successfully analysed.")
    raise SystemExit(1)

ranking = pd.DataFrame(results)

status_order = {
    "CANDIDATE": 3,
    "WATCH": 2,
    "WAIT": 1,
}

ranking["Status Rank"] = ranking["Status"].map(
    status_order
)

ranking = ranking.sort_values(
    by=[
        "Status Rank",
        "Entry Score",
        "Reward Risk",
        "Volume Ratio",
    ],
    ascending=[
        False,
        False,
        False,
        False,
    ],
).reset_index(drop=True)

# ============================================================
# Display ranked results
# ============================================================

print("\nRANKED SWING-TRADING SETUPS")
print("=" * 78)

for position, row in ranking.iterrows():
    print(f"\n#{position + 1} {row['Symbol']}")
    print("-" * 58)

    print(f"Data date          : {row['Data Date']}")
    print(f"Market condition   : {row['Market Status']}")
    print(f"Closing price      : ${row['Close']:.2f}")
    print(f"Trend              : {row['Trend']}")
    print(f"EMA20              : ${row['EMA20']:.2f}")
    print(f"EMA50              : ${row['EMA50']:.2f}")
    print(f"EMA200             : ${row['EMA200']:.2f}")
    print(
        f"Distance to EMA20  : "
        f"{row['EMA20 Distance %']:.2f}%"
    )
    print(
        f"Volume ratio       : "
        f"{row['Volume Ratio']:.2f}x"
    )
    print(
        f"Bullish candle     : "
        f"{row['Bullish Candle']}"
    )
    print(f"Entry score        : {row['Entry Score']}/100")

    print("\nENTRY PLAN")
    print(
        f"Suggested entry    : "
        f"${row['Suggested Entry']:.2f}"
    )
    print(
        "Entry method       : "
        "0.1% above latest candle high"
    )

    print("\nSTOP PLAN")
    print(f"Recent support     : ${row['Support']:.2f}")
    print(f"Swing stop         : ${row['Swing Stop']:.2f}")
    print(f"ATR14              : ${row['ATR14']:.2f}")
    print(f"ATR stop           : ${row['ATR Stop']:.2f}")
    print(
        f"Recommended stop   : "
        f"${row['Recommended Stop']:.2f}"
    )
    print(f"Selected method    : {row['Stop Method']}")
    print(
        f"Stop distance      : "
        f"${row['Stop Distance']:.2f} "
        f"({row['Stop Distance %']:.2f}%)"
    )

    print("\nTARGET AND REWARD")
    print(
        f"Recent resistance  : "
        f"${row['Resistance']:.2f}"
    )
    print(
        f"Potential reward   : "
        f"${row['Potential Reward']:.2f}"
    )
    print(
        f"Reward-to-risk     : "
        f"{row['Reward Risk']:.2f}R"
    )

    print("\nPOSITION SIZE")
    print(
        f"Suggested shares   : "
        f"{int(row['Position Size'])}"
    )
    print(
        f"Position value     : "
        f"RM{row['Position Value RM']:,.2f}"
    )
    print(
        f"Estimated loss     : "
        f"RM{row['Estimated Loss RM']:,.2f}"
    )
    print(
        f"Estimated profit   : "
        f"RM{row['Estimated Profit RM']:,.2f}"
    )

    print("\nDECISION")
    print(f"Status             : {row['Status']}")
    print(f"Positive factors   : {row['Positive Reasons']}")
    print(f"Warnings           : {row['Warnings']}")

print("\n" + "=" * 78)
print("Scanner completed.")
print("CANDIDATE means chart review is required; it is not an order signal.")
print("The model remains a prototype until its rules are backtested.")
print("=" * 78)