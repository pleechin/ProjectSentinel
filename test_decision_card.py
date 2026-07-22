from modules.decision_card import build_decision_card


def test_candidate_card_shows_both_sides():
    card = build_decision_card(
        decision="CANDIDATE",
        score_result={
            "Positive Factors": ["Bullish market", "Strong trend"],
            "Warnings": ["Volume is slightly weak"],
            "Next Action": ["Confirm breakout"],
        },
        stock={"Trend": "STRONG BULLISH"},
        trade_plan={
            "Suggested Entry": 100,
            "Recommended Stop": 95,
            "Resistance": 110,
            "Reward Risk": 2.0,
            "Position Size": 10,
        },
        market={"Status": "HEALTHY"},
    )
    assert card["Why Buy"] == ["Bullish market", "Strong trend"]
    assert card["Why Not Buy"] == ["Volume is slightly weak"]
    assert card["What To Watch"] == ["Confirm breakout"]
    assert card["Trade Plan"]["Entry"] == 100
    assert card["Invalidation"]


def test_wait_card_has_action():
    card = build_decision_card(
        decision="WAIT",
        score_result={"Positive Factors": [], "Warnings": [], "Next Action": []},
        stock={"Trend": "MIXED"},
        trade_plan={},
        market={"Status": "CAUTION"},
    )
    assert "Do not open" in card["Recommended Action"]
    assert card["Why Buy"]
    assert card["Why Not Buy"]
    assert card["What To Watch"]


if __name__ == "__main__":
    test_candidate_card_shows_both_sides()
    test_wait_card_has_action()
    print("Decision card tests passed.")
