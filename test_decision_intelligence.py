from modules.decision_intelligence import build_decision_intelligence, confidence_label


def test_high_quality_candidate():
    result = build_decision_intelligence(
        decision="CANDIDATE",
        score_result={"Score": 91, "Positive Factors": ["Strong trend"], "Warnings": []},
        stock={"Trend": "STRONG BULLISH", "Volume Ratio": 1.4, "EMA20 Distance %": 1.0, "Sector Score": 80, "Industry Score": 85},
        trade_plan={"Reward Risk": 3.0, "Stop Distance %": 4.0, "Risk Passes": True},
        market={"Score": 85, "Permission": True},
    )
    assert result["Confidence Label"] == "HIGH CONVICTION"
    assert result["Bull Case"]
    assert result["Risk Count"] == 0
    assert "bull case" in result["Devils Advocate Verdict"].lower()


def test_weak_setup_is_challenged():
    result = build_decision_intelligence(
        decision="WAIT",
        score_result={"Score": 40, "Positive Factors": [], "Warnings": ["Weak volume"]},
        stock={"Trend": "MIXED", "Volume Ratio": 0.7, "EMA20 Distance %": 7.0, "Sector Score": 35, "Industry Score": 40},
        trade_plan={"Reward Risk": 1.0, "Stop Distance %": 0, "Risk Passes": False},
        market={"Score": 40, "Permission": False},
    )
    assert confidence_label(40) == "AVOID FOR NOW"
    assert result["Risk Count"] >= 5
    assert "bear case" in result["Devils Advocate Verdict"].lower()


if __name__ == "__main__":
    test_high_quality_candidate()
    test_weak_setup_is_challenged()
    print("Decision intelligence tests passed.")
